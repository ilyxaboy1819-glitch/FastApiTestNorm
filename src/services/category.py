import logging
from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.category import CategoryModel
from src.schemas.category import CategoryBase, CategoryUpdate, CategoryRead
from src.exceptions import NotFoundException, AlreadyExistsException

logger = logging.getLogger(__name__)


class CategoryService:

    def __init__(self, session: AsyncSession):
        self.session = session

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

    async def create(self, data: CategoryBase) -> CategoryRead:
        existing = await self.session.execute(
            sa.select(CategoryModel).where(CategoryModel.name == data.name)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Category with name='{data.name}' already exists")
            raise AlreadyExistsException("Category with this name already exists")

        category = CategoryModel(**data.model_dump())
        self.session.add(category)
        await self.session.flush()
        logger.info(f"Category created with id={category.id}")
        return CategoryRead.model_validate({"id": category.id, "name": category.name, "description": category.description, "applications": []})

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[CategoryRead]:
        logger.info(f"Getting categories skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(CategoryModel)
            .options(selectinload(CategoryModel.applications))
            .offset(skip)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return [CategoryRead.model_validate(c) for c in result.scalars().all()]

    async def get_by_id(self, category_id: UUID) -> CategoryRead:
        category = await self._get_category_orm(category_id)
        return CategoryRead.model_validate(category)

    async def update(self, category_id: UUID, data: CategoryUpdate) -> CategoryRead:
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

    async def delete(self, category_id: UUID) -> None:
        category = await self._get_category_orm(category_id)
        await self.session.delete(category)
        logger.info(f"Category deleted with id={category_id}")

    @staticmethod
    def _update_fields(obj: CategoryModel, fields: dict) -> None:
        for field, value in fields.items():
            setattr(obj, field, value)
