import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
import pybreaker

from src.cache import delete_cached
from src.clients.order_service import OrderServiceClient
from src.db import SessionFactory
from src.exceptions import NotFoundException, OrderServiceError
from src.models.order import OrderStatus
from src.repositories.order import OrderRepository

logger = logging.getLogger(__name__)

STUCK_CHECK_INTERVAL = 60
STUCK_MINUTES = 5
MAX_RETRIES = 5
BASE_BACKOFF = 60
MAX_BACKOFF = 3600
MAX_CONCURRENT = 10
ORDER_CACHE_PREFIX = "order"

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
            expected_status=OrderStatus.NEW.value,
            external_id=external_id,
        )
        await session.commit()
    await delete_cached(f"{ORDER_CACHE_PREFIX}:{order_id}")


async def _mark_error(order_id: UUID, error: str) -> None:
    async with SessionFactory() as session:
        repo = OrderRepository(session)
        await repo.update_status(order_id, OrderStatus.ERROR.value, expected_status=OrderStatus.NEW.value)
        await repo.save_last_error(order_id, error)
        await session.commit()
    await delete_cached(f"{ORDER_CACHE_PREFIX}:{order_id}")


async def _increment_with_backoff(order_id: UUID, retry_count: int, error: str | None = None) -> None:
    backoff = min(BASE_BACKOFF * (2 ** retry_count), MAX_BACKOFF)
    jitter = random.uniform(0, backoff * 0.1)
    next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff + jitter)
    async with SessionFactory() as session:
        repo = OrderRepository(session)
        await repo.increment_retry(order_id, next_retry_at, last_error=error)
        await session.commit()


async def _process_stuck_order(client: OrderServiceClient, order_id: UUID, retry_count: int) -> None:
    if retry_count >= MAX_RETRIES:
        await _handle_max_retries(client, order_id)
        return

    try:
        remote = await client.get_order(order_id)
    except NotFoundException:
        await _increment_with_backoff(order_id, retry_count, error="not found in remote service")
        logger.info(f"Order {order_id} not found in remote, retry {retry_count + 1}/{MAX_RETRIES}")
        return
    except _NETWORK_ERRORS as e:
        await _increment_with_backoff(order_id, retry_count, error=str(e))
        logger.warning(f"Order {order_id} network error, retry {retry_count + 1}/{MAX_RETRIES}: {e}")
        return
    except Exception as e:
        await _mark_error(order_id, str(e))
        logger.error(f"Order {order_id} unexpected error, marked as ERROR: {e}")
        return

    await _apply_status(order_id, OrderStatus.CONFIRMED.value, external_id=remote.id)
    logger.info(f"Order {order_id} confirmed with external_id={remote.id}")


async def _handle_max_retries(client: OrderServiceClient, order_id: UUID) -> None:
    try:
        remote = await client.get_order(order_id)
    except NotFoundException:
        await _apply_status(order_id, OrderStatus.CANCELLED.value)
        logger.warning(f"Order {order_id} not found after max retries, CANCELLED")
        return
    except _NETWORK_ERRORS:
        await _apply_status(order_id, OrderStatus.FAILED.value)
        logger.warning(f"Order {order_id} unreachable after max retries, FAILED")
        return
    except Exception as e:
        logger.error(f"Order {order_id} unexpected error on final attempt, skipping: {e}")
        return

    await _apply_status(order_id, OrderStatus.CONFIRMED.value, external_id=remote.id)
    logger.info(f"Order {order_id} confirmed on final attempt with external_id={remote.id}")


async def _claim_and_fetch_orders() -> list[tuple[UUID, int]]:
    async with SessionFactory() as session:
        repo = OrderRepository(session)
        stuck_orders = await repo.get_stuck_orders(STUCK_MINUTES, MAX_RETRIES)
        orders_data = [(order.id, order.retry_count) for order in stuck_orders]
        for order in stuck_orders:
            await repo.claim(order.id)
        await session.commit()
    return orders_data


async def order_worker() -> None:
    client = OrderServiceClient()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def _limited(order_id: UUID, retry_count: int) -> None:
        async with semaphore:
            await _process_stuck_order(client, order_id, retry_count)

    while True:
        await asyncio.sleep(STUCK_CHECK_INTERVAL)
        try:
            orders_data = await _claim_and_fetch_orders()

            tasks = [_limited(oid, rc) for oid, rc in orders_data]
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Order worker error: {e}")
