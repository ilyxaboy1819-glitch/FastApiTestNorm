import logging
from uuid import UUID
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.application import ApplicationModel

logger = logging.getLogger(__name__)


class ApplicationRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, app: ApplicationModel) -> ApplicationModel:
        self.session.add(app)
        await self.session.flush()
        await self.session.refresh(app, ["comments"])
        return app

    async def get_by_id(self, app_id: UUID) -> Optional[ApplicationModel]:
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(selectinload(ApplicationModel.comments))
            .where(ApplicationModel.id == app_id, ApplicationModel.is_deleted == False)
            .with_for_update(skip_locked=True)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ApplicationModel]:
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(selectinload(ApplicationModel.comments))
            .where(ApplicationModel.is_deleted == False)
            .with_for_update(skip_locked=True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, app_id: UUID, fields: dict) -> None:
        await self.session.execute(
            sa.update(ApplicationModel)
            .where(ApplicationModel.id == app_id)
            .values(**fields)
        )

    async def soft_delete(self, app_id: UUID) -> None:
        await self.session.execute(
            sa.update(ApplicationModel)
            .where(ApplicationModel.id == app_id)
            .values(is_deleted=True)
        )

