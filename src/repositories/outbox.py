from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.outbox import OutboxModel


class OutboxRepository:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, record: OutboxModel) -> OutboxModel:
        self._session.add(record)
        await self._session.flush()
        return record

    async def get_unpublished(self, limit: int = 100) -> list[OutboxModel]:
        result = await self._session.execute(
            select(OutboxModel)
            .where(OutboxModel.published_at.is_(None))
            .order_by(OutboxModel.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_published_batch(self, record_ids: List[UUID]) -> None:
        await self._session.execute(
            update(OutboxModel)
            .where(OutboxModel.id.in_(record_ids))
            .values(published_at=datetime.now(timezone.utc))
        )
