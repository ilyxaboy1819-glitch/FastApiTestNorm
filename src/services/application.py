import logging
from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.application import ApplicationModel
from src.models.category import CategoryModel
from src.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationRead
from src.schemas.category import CategoryBase, CategoryUpdate, CategoryRead
from src.exceptions import NotFoundException, AlreadyExistsException

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

    async def create(self, data: ApplicationCreate) -> ApplicationRead:
        app = ApplicationModel.from_schema(data)
        self.session.add(app)
        await self.session.flush()
        logger.info(f"Application created with id={app.id}")
        await self.session.refresh(app, ["comments"])
        return ApplicationRead.model_validate(app)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ApplicationRead]:
        logger.info(f"Getting applications skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(selectinload(ApplicationModel.comments))
            .where(ApplicationModel.is_deleted == False)
            .offset(skip)
            .limit(limit)
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
        await self._get_app_orm(app_id)
        await self.session.execute(
            sa.update(ApplicationModel)
            .where(ApplicationModel.id == app_id)
            .values(is_deleted=True)
        )
        logger.info(f"Application soft deleted with id={app_id}")

    # --- Category CRUD ---

    async def _get_category_orm(self, category_id: UUID) -> CategoryModel:
        result = await self.session.execute(
            sa.select(CategoryModel)
            .options(selectinload(CategoryModel.applications))
            .where(CategoryModel.id == category_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            logger.warning(f"Category with id={category_id} not found")
            raise NotFoundException(f"Category with id={category_id} not found")
        return category

    async def create_category(self, data: CategoryBase) -> CategoryRead:
        existing = await self.session.execute(
            sa.select(CategoryModel).where(CategoryModel.name == data.name)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Category with name='{data.name}' already exists")
            raise AlreadyExistsException("Category with this name already exists")

        category = CategoryModel(**data.model_dump())
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category, ["applications"])
        logger.info(f"Category created with id={category.id}")
        return CategoryRead.model_validate(category)

    async def get_all_categories(self, skip: int = 0, limit: int = 100) -> List[CategoryRead]:
        logger.info(f"Getting categories skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(CategoryModel)
            .options(selectinload(CategoryModel.applications))
            .offset(skip)
            .limit(limit)
        )
        return [CategoryRead.model_validate(c) for c in result.scalars().all()]

    async def get_category_by_id(self, category_id: UUID) -> CategoryRead:
        category = await self._get_category_orm(category_id)
        return CategoryRead.model_validate(category)

    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> CategoryRead:
        existing = await self.session.execute(
            sa.select(CategoryModel).where(CategoryModel.name == data.name)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Category with name='{data.name}' already exists")
            raise AlreadyExistsException("Category with this name already exists")

        category = await self._get_category_orm(category_id)
        self._update_fields(category, data.model_dump(exclude_unset=True))
        logger.info(f"Category updated with id={category_id}")
        return CategoryRead.model_validate(category)

    async def delete_category(self, category_id: UUID) -> None:
        category = await self._get_category_orm(category_id)
        await self.session.delete(category)
        logger.info(f"Category deleted with id={category_id}")

    @staticmethod
    def _update_fields(obj, fields: dict) -> None:
        for field, value in fields.items():
            setattr(obj, field, value)
