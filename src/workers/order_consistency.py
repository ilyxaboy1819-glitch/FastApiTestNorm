import asyncio
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from src.clients.order_service import OrderServiceClient
from src.db import SessionFactory
from src.exceptions import NotFoundException
from src.models.order import OrderStatus
from src.repositories.order import OrderRepository

logger = logging.getLogger(__name__)

STUCK_CHECK_INTERVAL = 60
STUCK_MINUTES = 5
MAX_RETRIES = 5
BASE_BACKOFF = 60


async def _process_stuck_order(client: OrderServiceClient, order_id: UUID, retry_count: int) -> None:
    if retry_count >= MAX_RETRIES:
        async with SessionFactory() as session:
            repo = OrderRepository(session)
            await repo.update_status(order_id, OrderStatus.FAILED.value)
            await session.commit()
        logger.warning(f"Order {order_id} exceeded max retries, marked as FAILED")
        return

    try:
        remote = await client.get_order(order_id)
    except NotFoundException:
        async with SessionFactory() as session:
            repo = OrderRepository(session)
            await repo.update_status(order_id, OrderStatus.CANCELLED.value)
            await session.commit()
        logger.info(f"Order {order_id} not found in remote service, cancelled")
        return
    except Exception as e:
        next_retry_at = datetime.now(timezone.utc) + timedelta(
            seconds=BASE_BACKOFF * (2 ** retry_count)
        )
        async with SessionFactory() as session:
            repo = OrderRepository(session)
            await repo.increment_retry(order_id, next_retry_at)
            await session.commit()
        logger.warning(f"Order {order_id} retry {retry_count + 1}/{MAX_RETRIES}, next at {next_retry_at}: {e}")
        return

    async with SessionFactory() as session:
        repo = OrderRepository(session)
        await repo.update_status(order_id, OrderStatus.CONFIRMED.value, external_id=remote.id)
        await session.commit()
    logger.info(f"Order {order_id} confirmed with external_id={remote.id}")


async def order_consistency_worker() -> None:
    client = OrderServiceClient()
    while True:
        await asyncio.sleep(STUCK_CHECK_INTERVAL)
        try:
            async with SessionFactory() as session:
                repo = OrderRepository(session)
                stuck_orders = await repo.get_stuck_orders(STUCK_MINUTES, MAX_RETRIES)
                orders_data = [(order.id, order.retry_count) for order in stuck_orders]
                await session.commit()

            for order_id, retry_count in orders_data:
                await _process_stuck_order(client, order_id, retry_count)

        except Exception as e:
            logger.error(f"Consistency worker error: {e}")
