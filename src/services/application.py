import logging
from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.application import ApplicationModel
from src.models.category import CategoryModel
from src.models.user import UserModel
from src.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationRead
from src.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class ApplicationService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_app_orm(self, app_id: UUID) -> ApplicationModel:
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(
                selectinload(ApplicationModel.user),
                selectinload(ApplicationModel.category),
                selectinload(ApplicationModel.comments),
            )
            .where(ApplicationModel.id == app_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")
        return app

    async def create(self, data: ApplicationCreate) -> ApplicationRead:
        user = await self.session.get(UserModel, data.user_id)
        if not user:
            logger.warning(f"User with id={data.user_id} not found")
            raise ValidationException(field="user_id", message=f"User {data.user_id} does not exist")

        category = await self.session.get(CategoryModel, data.category_id)
        if not category:
            logger.warning(f"Category with id={data.category_id} not found")
            raise ValidationException(field="category_id", message=f"Category {data.category_id} does not exist")

        app = ApplicationModel(**data.model_dump())
        app.user = user
        app.category = category
        self.session.add(app)

        logger.info(f"Application created with id={app.id}")
        return ApplicationRead.model_validate(app)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ApplicationRead]:
        logger.info(f"Getting applications skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(
                selectinload(ApplicationModel.user),
                selectinload(ApplicationModel.category),
                selectinload(ApplicationModel.comments),
            )
            .offset(skip)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return [ApplicationRead.model_validate(app) for app in result.scalars().all()]

    async def get_by_id(self, app_id: UUID) -> ApplicationRead:
        app = await self._get_app_orm(app_id)
        return ApplicationRead.model_validate(app)

    async def update(self, app_id: UUID, data: ApplicationUpdate) -> ApplicationRead:
        app = await self._get_app_orm(app_id)

        category = await self.session.get(CategoryModel, data.category_id)
        if not category:
            logger.warning(f"Category with id={data.category_id} not found")
            raise ValidationException(field="category_id", message=f"Category {data.category_id} does not exist")

        app.category = category
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(app, field, value)

        logger.info(f"Application updated with id={app_id}")
        return ApplicationRead.model_validate(app)

    async def delete(self, app_id: UUID) -> None:
        app = await self.session.get(ApplicationModel, app_id)
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")
        await self.session.delete(app)
        logger.info(f"Application deleted with id={app_id}")
