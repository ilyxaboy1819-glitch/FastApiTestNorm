import asyncio
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
import pybreaker

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

_NETWORK_ERRORS = (
    httpx.ConnectError,
    httpx.TimeoutException,
    OrderServiceError,
    pybreaker.CircuitBreakerError,
)


async def _increment_with_backoff(order_id: UUID, retry_count: int) -> None:
    backoff = min(BASE_BACKOFF * (2 ** retry_count), MAX_BACKOFF)
    next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff)
    async with SessionFactory() as session:
        repo = OrderRepository(session)
        await repo.increment_retry(order_id, next_retry_at)
        await session.commit()


async def _mark_final_status(client: OrderServiceClient, order_id: UUID) -> None:
    try:
        remote = await client.get_order(order_id)
    except NotFoundException:
        async with SessionFactory() as session:
            repo = OrderRepository(session)
            await repo.update_status(order_id, OrderStatus.CANCELLED.value)
            await session.commit()
        logger.warning(f"Order {order_id} not found after max retries, marked as CANCELLED")
        return
    except Exception:
        async with SessionFactory() as session:
            repo = OrderRepository(session)
            await repo.update_status(order_id, OrderStatus.FAILED.value)
            await session.commit()
        logger.warning(f"Order {order_id} unreachable after max retries, marked as FAILED")
        return

    async with SessionFactory() as session:
        repo = OrderRepository(session)
        await repo.update_status(order_id, OrderStatus.CONFIRMED.value, external_id=remote.id)
        await session.commit()
    logger.info(f"Order {order_id} confirmed on final attempt with external_id={remote.id}")


async def _process_stuck_order(client: OrderServiceClient, order_id: UUID, retry_count: int) -> None:
    if retry_count >= MAX_RETRIES:
        await _mark_final_status(client, order_id)
        return

    try:
        remote = await client.get_order(order_id)
    except NotFoundException:
        await _increment_with_backoff(order_id, retry_count)
        logger.info(f"Order {order_id} not found in remote, retry {retry_count + 1}/{MAX_RETRIES}")
        return
    except _NETWORK_ERRORS as e:
        await _increment_with_backoff(order_id, retry_count)
        logger.warning(f"Order {order_id} network error, retry {retry_count + 1}/{MAX_RETRIES}: {e}")
        return
    except Exception as e:
        logger.error(f"Order {order_id} unexpected error, skipping: {e}")
        return

    async with SessionFactory() as session:
        repo = OrderRepository(session)
        await repo.update_status(order_id, OrderStatus.CONFIRMED.value, external_id=remote.id)
        await session.commit()
    logger.info(f"Order {order_id} confirmed with external_id={remote.id}")


async def order_worker() -> None:
    client = OrderServiceClient()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def _limited(order_id: UUID, retry_count: int) -> None:
        async with semaphore:
            await _process_stuck_order(client, order_id, retry_count)

    while True:
        await asyncio.sleep(STUCK_CHECK_INTERVAL)
        try:
            async with SessionFactory() as session:
                repo = OrderRepository(session)
                stuck_orders = await repo.get_stuck_orders(STUCK_MINUTES, MAX_RETRIES)
                orders_data = [(order.id, order.retry_count) for order in stuck_orders]
                await session.commit()

            tasks = [_limited(oid, rc) for oid, rc in orders_data]
            await asyncio.gather(*tasks)

        except Exception as e:
            logger.error(f"Order worker error: {e}")
