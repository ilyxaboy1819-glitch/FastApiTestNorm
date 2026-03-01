from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import List
import sqlalchemy as sa

from src.db import get_session
from src.models.category import CategoryModel
from src.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(tags=["Categories"])


@router.post('/categories', response_model=CategoryRead)
async def create_category(cat_data: CategoryCreate):
    async with get_session() as session:
        # Проверяем, нет ли категории с таким именем
        existing = await session.execute(
            sa.select(CategoryModel).where(CategoryModel.name == cat_data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Category with this name already exists")

        category = CategoryModel(**cat_data.dict())
        session.add(category)
        await session.flush()
        await session.refresh(category)
        return category


@router.get('/categories/{cat_id}', response_model=CategoryRead)
async def get_category(cat_id: UUID):
    async with get_session() as session:
        category = await session.get(CategoryModel, cat_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category


@router.get('/categories', response_model=List[CategoryRead])
async def get_categories(skip: int = 0, limit: int = 100):
    async with get_session() as session:
        categories = await session.execute(
            sa.select(CategoryModel).offset(skip).limit(limit)
        )
        return categories.scalars().all()


@router.put('/categories/{cat_id}', response_model=CategoryRead)
async def update_category(cat_id: UUID, cat_data: CategoryUpdate):
    async with get_session() as session:
        category = await session.get(CategoryModel, cat_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        for field, value in cat_data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        await session.flush()
        await session.refresh(category)
        return category


@router.delete('/categories/{cat_id}', status_code=204)
async def delete_category(cat_id: UUID):
    async with get_session() as session:
        category = await session.get(CategoryModel, cat_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        await session.delete(category)
        await session.flush()
        return None