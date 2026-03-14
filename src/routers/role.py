from fastapi import APIRouter, Depends, Response, Query
from uuid import UUID
from typing import List
from http import HTTPStatus

from src.dependencies import get_role_service
from src.schemas.role import RoleCreate, RoleRead, RoleUpdate
from src.services.role import RoleService

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])


@router.post("/", response_model=RoleRead, status_code=HTTPStatus.CREATED)
async def create_role(
    data: RoleCreate,
    service: RoleService = Depends(get_role_service),
) -> RoleRead:
    return await service.create(data)


@router.get("/", response_model=List[RoleRead], status_code=HTTPStatus.OK)
async def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: RoleService = Depends(get_role_service),
) -> List[RoleRead]:
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleRead, status_code=HTTPStatus.OK)
async def get_role(
    role_id: UUID,
    service: RoleService = Depends(get_role_service),
) -> RoleRead:
    return await service.get_by_id(role_id)


@router.put("/{role_id}", response_model=RoleRead, status_code=HTTPStatus.OK)
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