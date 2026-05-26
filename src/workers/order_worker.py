import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
import pybreaker

from src.clients.order_service import OrderServiceClient
from src.db import SessionFactory
from src.exceptions import NotFoundException, OrderServiceError
from src.models.order import LocalOrderModel, OrderStatus
from src.repositories.order import OrderRepository
from src.schemas.order import OrderPayload

logger = logging.getLogger(__name__)

STUCK_CHECK_INTERVAL = 60
STUCK_MINUTES = 5
MAX_RETRIES = 5
BASE_BACKOFF = 60
MAX_BACKOFF = 3600
MAX_CONCURRENT = 10

_NETWORK_ERRORS = (
    httpx.ConnectError,
    httpx.TimeoutException,
    OrderServiceError,
    pybreaker.CircuitBreakerError,
)


async def _apply_status(order_id: UUID, status: str, external_id: UUID = None) -> None:
    async with SessionFactory() as session:
        repo = OrderRepository(session)
        await repo.update_status(
            order_id, status,
            expected_status=OrderStatus.PENDING.value,
            external_id=external_id,
        )
        await session.commit()


async def _mark_error(order_id: UUID, error: str) -> None:
    async with SessionFactory() as session:
        repo = OrderRepository(session)
        await repo.update_status(order_id, OrderStatus.ERROR.value, expected_status=OrderStatus.PENDING.value)
        await repo.save_last_error(order_id, error)
        await session.commit()


async def _increment_with_backoff(order_id: UUID, retry_count: int, error: str | None = None) -> None:
    backoff = min(BASE_BACKOFF * (2 ** retry_count), MAX_BACKOFF)
    jitter = random.uniform(0, backoff * 0.1)
    next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff + jitter)
    async with SessionFactory() as session:
        repo = OrderRepository(session)
        await repo.increment_retry(order_id, next_retry_at, last_error=error)
        await session.commit()


async def _process_stuck_order(client: OrderServiceClient, order: LocalOrderModel) -> None:
    if order.retry_count >= MAX_RETRIES:
        await _handle_max_retries(client, order)
        return

    if order.external_id:
        await _process_with_external_id(client, order)
    else:
        await _process_without_external_id(client, order)


async def _process_with_external_id(client: OrderServiceClient, order: LocalOrderModel) -> None:
    try:
        remote = await client.get_order(order.external_id)
    except NotFoundException:
        await _increment_with_backoff(order.id, order.retry_count, error="not found in remote service")
        logger.info(f"Order {order.id} not found in remote, retry {order.retry_count + 1}/{MAX_RETRIES}")
        return
    except _NETWORK_ERRORS as e:
        await _increment_with_backoff(order.id, order.retry_count, error=str(e))
        logger.warning(f"Order {order.id} network error, retry {order.retry_count + 1}/{MAX_RETRIES}: {e}")
        return
    except Exception as e:
        await _mark_error(order.id, str(e))
        logger.error(f"Order {order.id} unexpected error, marked as ERROR: {e}")
        return

    await _apply_status(order.id, OrderStatus.CONFIRMED.value, external_id=remote.id)
    logger.info(f"Order {order.id} confirmed with external_id={remote.id}")


async def _process_without_external_id(client: OrderServiceClient, order: LocalOrderModel) -> None:
    if not order.payload_json:
        await _mark_error(order.id, "no external_id and no payload to retry create")
        logger.error(f"Order {order.id} has no external_id and no payload, marked as ERROR")
        return

    payload = OrderPayload.model_validate_json(order.payload_json)

    try:
        remote = await client.create_order(payload)
    except _NETWORK_ERRORS as e:
        await _increment_with_backoff(order.id, order.retry_count, error=str(e))
        logger.warning(f"Order {order.id} create retry failed, retry {order.retry_count + 1}/{MAX_RETRIES}: {e}")
        return
    except Exception as e:
        await _mark_error(order.id, str(e))
        logger.error(f"Order {order.id} unexpected error on create retry, marked as ERROR: {e}")
        return

    await _apply_status(order.id, OrderStatus.CONFIRMED.value, external_id=remote.id)
    logger.info(f"Order {order.id} created on retry with external_id={remote.id}")


async def _handle_max_retries(client: OrderServiceClient, order: LocalOrderModel) -> None:
    if order.external_id:
        await _handle_max_retries_with_id(client, order)
    else:
        await _handle_max_retries_without_id(client, order)


async def _handle_max_retries_with_id(client: OrderServiceClient, order: LocalOrderModel) -> None:
    try:
        remote = await client.get_order(order.external_id)
    except NotFoundException:
        await _apply_status(order.id, OrderStatus.CANCELLED.value)
        logger.warning(f"Order {order.id} not found after max retries, CANCELLED")
        return
    except _NETWORK_ERRORS:
        await _apply_status(order.id, OrderStatus.FAILED.value)
        logger.warning(f"Order {order.id} unreachable after max retries, FAILED")
        return
    except Exception as e:
        await _mark_error(order.id, str(e))
        logger.error(f"Order {order.id} unexpected error on final attempt, marked as ERROR: {e}")
        return

    await _apply_status(order.id, OrderStatus.CONFIRMED.value, external_id=remote.id)
    logger.info(f"Order {order.id} confirmed on final attempt with external_id={remote.id}")


async def _handle_max_retries_without_id(client: OrderServiceClient, order: LocalOrderModel) -> None:
    if not order.payload_json:
        await _mark_error(order.id, "max retries reached, no external_id and no payload")
        logger.error(f"Order {order.id} max retries, no payload, marked as ERROR")
        return

    payload = OrderPayload.model_validate_json(order.payload_json)

    try:
        remote = await client.create_order(payload)
    except _NETWORK_ERRORS:
        await _apply_status(order.id, OrderStatus.FAILED.value)
        logger.warning(f"Order {order.id} create failed after max retries, FAILED")
        return
    except Exception as e:
        await _mark_error(order.id, str(e))
        logger.error(f"Order {order.id} unexpected error on final create attempt, marked as ERROR: {e}")
        return

    await _apply_status(order.id, OrderStatus.CONFIRMED.value, external_id=remote.id)
    logger.info(f"Order {order.id} created on final attempt with external_id={remote.id}")


async def _claim_and_fetch_orders() -> list[LocalOrderModel]:
    async with SessionFactory() as session:
        repo = OrderRepository(session)
        stuck_orders = await repo.get_stuck_orders(STUCK_MINUTES, MAX_RETRIES)
        for order in stuck_orders:
            await repo.claim(order.id)
        await session.commit()
    return stuck_orders


async def order_worker() -> None:
    client = OrderServiceClient()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def _limited(order: LocalOrderModel) -> None:
        async with semaphore:
            await _process_stuck_order(client, order)

    while True:
        await asyncio.sleep(STUCK_CHECK_INTERVAL)
        try:
            orders = await _claim_and_fetch_orders()

            tasks = [_limited(o) for o in orders]
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Order worker error: {e}")
