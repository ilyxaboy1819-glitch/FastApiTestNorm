from fastapi import APIRouter, Depends, Response
from uuid import UUID
from typing import List
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate
from src.services.profile import ProfileService

router = APIRouter(prefix="/api/v1/profiles", tags=["Profiles"])


def get_profile_service(session: AsyncSession = Depends(get_session)) -> ProfileService:
    return ProfileService(session)


@router.post("/", response_model=ProfileRead, status_code=HTTPStatus.CREATED)
async def create_profile(
    data: ProfileCreate,
    service: ProfileService = Depends(get_profile_service),
) -> ProfileRead:
    return await service.create(data)


@router.get("/", response_model=List[ProfileRead], status_code=HTTPStatus.OK)
async def get_profiles(
    skip: int = 0,
    limit: int = 100,
    service: ProfileService = Depends(get_profile_service),
) -> List[ProfileRead]:
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{profile_id}", response_model=ProfileRead, status_code=HTTPStatus.OK)
async def get_profile(
    profile_id: UUID,
    service: ProfileService = Depends(get_profile_service),
) -> ProfileRead:
    return await service.get_by_id(profile_id)


@router.put("/{profile_id}", response_model=ProfileRead, status_code=HTTPStatus.OK)
async def update_profile(
    profile_id: UUID,
    data: ProfileUpdate,
    service: ProfileService = Depends(get_profile_service),
) -> ProfileRead:
    return await service.update(profile_id, data)


@router.delete("/{profile_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_profile(
    profile_id: UUID,
    service: ProfileService = Depends(get_profile_service),
) -> Response:
    await service.delete(profile_id)
    return Response(status_code=HTTPStatus.NO_CONTENT)