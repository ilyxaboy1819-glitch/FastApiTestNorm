import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.order import LocalOrderModel, OrderStatus

logger = logging.getLogger(__name__)


class OrderRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: LocalOrderModel) -> LocalOrderModel:
        self.session.add(order)
        await self.session.flush()
        return order

    async def get_by_id(self, order_id: UUID) -> Optional[LocalOrderModel]:
        result = await self.session.execute(
            sa.select(LocalOrderModel)
            .where(LocalOrderModel.id == order_id, LocalOrderModel.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        order_id: UUID,
        status: str,
        expected_status: str | None = None,
        external_id: UUID | None = None,
    ) -> None:
        conditions = [LocalOrderModel.id == order_id]
        if expected_status is not None:
            conditions.append(LocalOrderModel.status == expected_status)

        values = {"status": status}
        if external_id is not None:
            values["external_id"] = external_id

        await self.session.execute(
            sa.update(LocalOrderModel)
            .where(*conditions)
            .values(**values)
        )
        await self.session.flush()

    async def increment_retry(
        self, order_id: UUID, next_retry_at: datetime, last_error: str | None = None
    ) -> None:
        values = {
            "retry_count": LocalOrderModel.retry_count + 1,
            "next_retry_at": next_retry_at,
        }
        if last_error is not None:
            values["last_error"] = last_error
        await self.session.execute(
            sa.update(LocalOrderModel)
            .where(
                LocalOrderModel.id == order_id,
                LocalOrderModel.status == OrderStatus.NEW.value,
            )
            .values(**values)
        )
        await self.session.flush()

    async def claim(self, order_id: UUID) -> None:
        await self.session.execute(
            sa.update(LocalOrderModel)
            .where(LocalOrderModel.id == order_id)
            .values(claimed_at=datetime.now(timezone.utc))
        )
        await self.session.flush()

    async def save_last_error(self, order_id: UUID, error: str) -> None:
        await self.session.execute(
            sa.update(LocalOrderModel)
            .where(LocalOrderModel.id == order_id)
            .values(last_error=error)
        )
        await self.session.flush()

    async def get_stuck_orders(
        self, stuck_minutes: int = 5, max_retries: int = 5, limit: int = 50
    ) -> List[LocalOrderModel]:
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(minutes=stuck_minutes)
        result = await self.session.execute(
            sa.select(LocalOrderModel)
            .where(
                LocalOrderModel.status == OrderStatus.NEW.value,
                LocalOrderModel.is_deleted == False,
                LocalOrderModel.created_at < threshold,
                LocalOrderModel.retry_count < max_retries,
                sa.or_(
                    LocalOrderModel.next_retry_at == None,
                    LocalOrderModel.next_retry_at <= now,
                ),
                sa.or_(
                    LocalOrderModel.claimed_at == None,
                    LocalOrderModel.claimed_at < threshold,
                ),
            )
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        return list(result.scalars().all())
