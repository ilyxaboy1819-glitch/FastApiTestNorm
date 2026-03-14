from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import List
from http import HTTPStatus

from src.dependencies import get_application_service
from src.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from src.services.application import ApplicationService

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@router.post("/", response_model=CategoryRead, status_code=HTTPStatus.CREATED)
async def create_category(
    data: CategoryCreate,
    service: ApplicationService = Depends(get_application_service),
) -> CategoryRead:
    return await service.create_category(data)


@router.get("/", response_model=List[CategoryRead], status_code=HTTPStatus.OK)
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: ApplicationService = Depends(get_application_service),
) -> List[CategoryRead]:
    return await service.get_all_categories(skip=skip, limit=limit)


@router.get("/{cat_id}", response_model=CategoryRead, status_code=HTTPStatus.OK)
async def get_category(
    cat_id: UUID,
    service: ApplicationService = Depends(get_application_service),
) -> CategoryRead:
    return await service.get_category_by_id(cat_id)


@router.put("/{cat_id}", response_model=CategoryRead, status_code=HTTPStatus.OK)
async def update_category(
    cat_id: UUID,
    data: CategoryUpdate,
    service: ApplicationService = Depends(get_application_service),
) -> CategoryRead:
    return await service.update_category(cat_id, data)


@router.delete("/{cat_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_category(
    cat_id: UUID,
    service: ApplicationService = Depends(get_application_service),
) -> None:
    await service.delete_category(cat_id)