import logging
from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.application import ApplicationModel
from src.models.comment import CommentModel
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
            .where(ApplicationModel.id == app_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")
        return app

    async def create(self, data: ApplicationCreate) -> ApplicationRead:
        app = ApplicationModel(**data.model_dump(exclude={"comments"}))
        self.session.add(app)
        await self.session.flush()

        for comment_data in data.comments:
            comment = CommentModel(**comment_data.model_dump(), application_id=app.id)
            self.session.add(comment)

        logger.info(f"Application created with id={app.id}")
        return await self._get_app_orm(app.id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ApplicationRead]:
        logger.info(f"Getting applications skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(selectinload(ApplicationModel.comments))
            .offset(skip)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return [ApplicationRead.model_validate(app) for app in result.scalars().all()]

    async def get_by_id(self, app_id: UUID) -> ApplicationRead:
        app = await self._get_app_orm(app_id)
        return ApplicationRead.model_validate(app)

    async def update(self, app_id: UUID, data: ApplicationUpdate) -> ApplicationRead:
        await self.session.execute(
            sa.update(ApplicationModel)
            .where(ApplicationModel.id == app_id)
            .values(**data.model_dump(exclude_unset=True))
        )
        logger.info(f"Application updated with id={app_id}")
        return await self.get_by_id(app_id)

    async def delete(self, app_id: UUID) -> None:
        app = await self._get_app_orm(app_id)
        await self.session.delete(app)
        logger.info(f"Application deleted with id={app_id}")
