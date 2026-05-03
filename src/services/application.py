import logging
from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.application import ApplicationModel
from src.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationRead
from src.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class ApplicationService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_app_orm(self, app_id: UUID) -> ApplicationModel:
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(selectinload(ApplicationModel.comments))
            .where(ApplicationModel.id == app_id, ApplicationModel.is_deleted == False)
        )
        app = result.scalar_one_or_none()
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")
        return app

    async def create(self, data: ApplicationCreate, user_id: UUID, category_id: UUID) -> ApplicationRead:
        app = data.to_model(user_id, category_id)
        self.session.add(app)
        await self.session.flush()
        logger.info(f"Application created with id={app.id}")
        await self.session.refresh(app, ["comments"])
        return ApplicationRead.from_model(app)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ApplicationRead]:
        logger.info(f"Getting applications skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(selectinload(ApplicationModel.comments))
            .where(ApplicationModel.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return ApplicationRead.from_list(result.scalars().all())

    async def get_by_id(self, app_id: UUID) -> ApplicationRead:
        app = await self._get_app_orm(app_id)
        return ApplicationRead.from_model(app)

    async def update(self, app_id: UUID, data: ApplicationUpdate, category_id: UUID) -> ApplicationRead:
        await self.session.execute(
            sa.update(ApplicationModel)
            .where(ApplicationModel.id == app_id)
            .values(**data.model_dump(exclude_unset=True), category_id=category_id)
        )
        logger.info(f"Application updated with id={app_id}")
        return await self.get_by_id(app_id)

    async def delete(self, app_id: UUID) -> None:
        await self._get_app_orm(app_id)
        await self.session.execute(
            sa.update(ApplicationModel)
            .where(ApplicationModel.id == app_id)
            .values(is_deleted=True)
        )
        logger.info(f"Application soft deleted with id={app_id}")
