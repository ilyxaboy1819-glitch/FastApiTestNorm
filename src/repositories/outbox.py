from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.outbox import OutboxModel, OutboxStatus


class OutboxRepository:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, record: OutboxModel) -> OutboxModel:
        self._session.add(record)
        await self._session.flush()
        return record

    async def claim_batch(self, limit: int = 100) -> list[OutboxModel]:
        result = await self._session.execute(
            select(OutboxModel)
            .where(OutboxModel.status == OutboxStatus.PENDING.value)
            .order_by(OutboxModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        records = list(result.scalars().all())
        if records:
            await self._session.execute(
                update(OutboxModel)
                .where(OutboxModel.id.in_([r.id for r in records]))
                .values(status=OutboxStatus.PROCESSING.value)
            )
            await self._session.flush()
        return records

    async def mark_published_batch(self, record_ids: List[UUID]) -> None:
        await self._session.execute(
            update(OutboxModel)
            .where(OutboxModel.id.in_(record_ids))
            .values(
                status=OutboxStatus.PUBLISHED.value,
                published_at=datetime.now(timezone.utc),
            )
        )

    async def release_batch(self, record_ids: List[UUID]) -> None:
        await self._session.execute(
            update(OutboxModel)
            .where(OutboxModel.id.in_(record_ids))
            .values(status=OutboxStatus.PENDING.value)
        )
