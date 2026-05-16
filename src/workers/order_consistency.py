import asyncio
import logging

from src.clients.order_service import OrderServiceClient
from src.db import SessionFactory
from src.models.order import OrderStatus
from src.repositories.order import OrderRepository

logger = logging.getLogger(__name__)

STUCK_CHECK_INTERVAL = 60
STUCK_MINUTES = 5


async def order_consistency_worker() -> None:
    client = OrderServiceClient()
    while True:
        await asyncio.sleep(STUCK_CHECK_INTERVAL)
        try:
            async with SessionFactory() as session:
                repo = OrderRepository(session)
                stuck_orders = await repo.get_stuck_orders(STUCK_MINUTES)

                for order in stuck_orders:
                    try:
                        remote = await client.get_order(order.id)
                        await repo.update_status(
                            order.id,
                            OrderStatus.CONFIRMED.value,
                            external_id=remote.id,
                        )
                        logger.info(f"Consistency worker: order {order.id} confirmed")
                    except Exception:
                        await repo.update_status(
                            order.id,
                            OrderStatus.CANCELLED.value,
                        )
                        logger.warning(f"Consistency worker: order {order.id} cancelled")

                await session.commit()
        except Exception as e:
            logger.error(f"Consistency worker error: {e}")
