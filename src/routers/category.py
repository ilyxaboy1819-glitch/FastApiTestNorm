from fastapi import APIRouter, Depends, Response
from uuid import UUID
from typing import List
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from src.services.category import CategoryService

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


def get_category_service(session: AsyncSession = Depends(get_session)) -> CategoryService:
    return CategoryService(session)


@router.post("/", response_model=CategoryRead, status_code=HTTPStatus.CREATED)
async def create_category(
    data: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
) -> CategoryRead:
    return await service.create(data)


@router.get("/", response_model=List[CategoryRead], status_code=HTTPStatus.OK)
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    service: CategoryService = Depends(get_category_service),
) -> List[CategoryRead]:
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{cat_id}", response_model=CategoryRead, status_code=HTTPStatus.OK)
async def get_category(
    cat_id: UUID,
    service: CategoryService = Depends(get_category_service),
) -> CategoryRead:
    return await service.get_by_id(cat_id)


@router.put("/{cat_id}", response_model=CategoryRead, status_code=HTTPStatus.OK)
async def update_category(
    cat_id: UUID,
    data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
) -> CategoryRead:
    return await service.update(cat_id, data)


@router.delete("/{cat_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_category(
    cat_id: UUID,
    service: CategoryService = Depends(get_category_service),
) -> Response:
    await service.delete(cat_id)
    return Response(status_code=HTTPStatus.NO_CONTENT)