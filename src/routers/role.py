from fastapi import APIRouter, Depends, Response
from uuid import UUID
from typing import List
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.schemas.role import RoleCreate, RoleRead, RoleUpdate
from src.services.role import RoleService

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])


def get_role_service(session: AsyncSession = Depends(get_session)) -> RoleService:
    return RoleService(session)


@router.post("/", response_model=RoleRead, status_code=HTTPStatus.CREATED)
async def create_role(
    data: RoleCreate,
    service: RoleService = Depends(get_role_service),
) -> RoleRead:
    return await service.create(data)


@router.get("/", response_model=List[RoleRead], status_code=HTTPStatus.OK)
async def get_roles(
    skip: int = 0,
    limit: int = 100,
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
) -> Response:
    await service.delete(role_id)
    return Response(status_code=HTTPStatus.NO_CONTENT)