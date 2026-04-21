from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import List
from http import HTTPStatus

from src.dependencies import get_role_service, get_category_service
from src.schemas.role import RoleCreate, RoleRead, RoleUpdate
from src.schemas.category import CategoryBase, CategoryRead, CategoryUpdate
from src.services.role import RoleService
from src.services.category import CategoryService

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])
category_router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@router.post("/", response_model=RoleRead, status_code=HTTPStatus.CREATED)
async def create_role(
    data: RoleCreate,
    service: RoleService = Depends(get_role_service),
) -> RoleRead:
    return await service.create(data)


@router.get("/", response_model=List[RoleRead])
async def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: RoleService = Depends(get_role_service),
) -> List[RoleRead]:
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleRead)
async def get_role(
    role_id: UUID,
    service: RoleService = Depends(get_role_service),
) -> RoleRead:
    return await service.get_by_id(role_id)


@router.put("/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: UUID,
    data: RoleUpdate,
    service: RoleService = Depends(get_role_service),
) -> RoleRead:
    return await service.update(role_id, data)


@router.delete("/{role_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_role(
    role_id: UUID,
    service: RoleService = Depends(get_role_service),
) -> None:
    await service.delete(role_id)


@category_router.post("/", response_model=CategoryRead, status_code=HTTPStatus.CREATED)
async def create_category(
    data: CategoryBase,
    service: CategoryService = Depends(get_category_service),
) -> CategoryRead:
    return await service.create(data)


@category_router.get("/", response_model=List[CategoryRead])
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: CategoryService = Depends(get_category_service),
) -> List[CategoryRead]:
    return await service.get_all(skip=skip, limit=limit)


@category_router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
) -> CategoryRead:
    return await service.get_by_id(category_id)


@category_router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
) -> CategoryRead:
    return await service.update(category_id, data)


@category_router.delete("/{category_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
) -> None:
    await service.delete(category_id)
