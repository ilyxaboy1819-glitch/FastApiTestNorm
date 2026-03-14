from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import List
from http import HTTPStatus

from src.dependencies import get_user_service
from src.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate
from src.services.user import UserService

router = APIRouter(prefix="/api/v1/profiles", tags=["Profiles"])


@router.post("/", response_model=ProfileRead, status_code=HTTPStatus.CREATED)
async def create_profile(
    data: ProfileCreate,
    service: UserService = Depends(get_user_service),
) -> ProfileRead:
    return await service.create_profile(data)


@router.get("/", response_model=List[ProfileRead], status_code=HTTPStatus.OK)
async def get_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: UserService = Depends(get_user_service),
) -> List[ProfileRead]:
    return await service.get_all_profiles(skip=skip, limit=limit)


@router.get("/{profile_id}", response_model=ProfileRead, status_code=HTTPStatus.OK)
async def get_profile(
    profile_id: UUID,
    service: UserService = Depends(get_user_service),
) -> ProfileRead:
    return await service.get_profile_by_id(profile_id)


@router.put("/{profile_id}", response_model=ProfileRead, status_code=HTTPStatus.OK)
async def update_profile(
    profile_id: UUID,
    data: ProfileUpdate,
    service: UserService = Depends(get_user_service),
) -> ProfileRead:
    return await service.update_profile(profile_id, data)


@router.delete("/{profile_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_profile(
    profile_id: UUID,
    service: UserService = Depends(get_user_service),
) -> None:
    await service.delete_profile(profile_id)