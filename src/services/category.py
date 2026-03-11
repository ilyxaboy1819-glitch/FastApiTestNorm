from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.category import CategoryModel
from src.schemas.category import CategoryCreate, CategoryUpdate
from src.exceptions import NotFoundException, AlreadyExistsException


class CategoryService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: CategoryCreate) -> CategoryModel:
        existing = await self.session.execute(
            sa.select(CategoryModel).where(CategoryModel.name == data.name)
        )
        if existing.scalar_one_or_none():
            raise AlreadyExistsException("Category with this name already exists")

        category = CategoryModel(**data.model_dump())
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[CategoryModel]:
        result = await self.session.execute(
            sa.select(CategoryModel).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, cat_id: UUID) -> CategoryModel:
        category = await self.session.get(CategoryModel, cat_id)
        if not category:
            raise NotFoundException("Category not found")
        return category

    async def update(self, cat_id: UUID, data: CategoryUpdate) -> CategoryModel:
        category = await self.session.get(CategoryModel, cat_id)
        if not category:
            raise NotFoundException("Category not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def delete(self, cat_id: UUID) -> None:
        category = await self.session.get(CategoryModel, cat_id)
        if not category:
            raise NotFoundException("Category not found")
        await self.session.delete(category)