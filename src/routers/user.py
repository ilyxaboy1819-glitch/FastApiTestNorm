from fastapi import APIRouter, Depends, Response
from uuid import UUID
from typing import List
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_session
from src.schemas.user import UserCreate, UserRead, UserUpdate
from src.services.user import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)


@router.post("/", response_model=UserRead, status_code=HTTPStatus.CREATED)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.create(data)


@router.get("/", response_model=List[UserRead], status_code=HTTPStatus.OK)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service),
) -> List[UserRead]:
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead, status_code=HTTPStatus.OK)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.get_by_id(user_id)


@router.put("/{user_id}", response_model=UserRead, status_code=HTTPStatus.OK)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.update(user_id, data)


@router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> Response:
    await service.delete(user_id)
    return Response(status_code=HTTPStatus.NO_CONTENT)