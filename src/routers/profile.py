from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import List
import sqlalchemy as sa
from src.db import get_session
from src.models.profile import ProfileModel
from src.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate


router = APIRouter(
    prefix="/profiles",tags=["Profiles"])


@router.post("/", response_model=ProfileRead)
async def create_profile(profile_data: ProfileCreate):
    async with get_session() as session:

        existing = await session.execute(
            sa.select(ProfileModel).where(
                ProfileModel.user_id == profile_data.user_id
            )
        )

        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Profile for this user already exists"
            )

        profile = ProfileModel(**profile_data.model_dump())
        session.add(profile)

        await session.commit()
        await session.refresh(profile)

        return profile


@router.get("/", response_model=List[ProfileRead])
async def get_profiles(skip: int = 0, limit: int = 100):
    async with get_session() as session:

        profiles = await session.execute(
            sa.select(ProfileModel)
            .offset(skip)
            .limit(limit)
        )

        return profiles.scalars().all()


@router.get("/{profile_id}", response_model=ProfileRead)
async def get_profile(profile_id: UUID):
    async with get_session() as session:

        profile = await session.get(ProfileModel, profile_id)

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        return profile


@router.put("/{profile_id}", response_model=ProfileRead)
async def update_profile(profile_id: UUID, profile_data: ProfileUpdate):
    async with get_session() as session:

        profile = await session.get(ProfileModel, profile_id)

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        for field, value in profile_data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)

        await session.commit()
        await session.refresh(profile)

        return profile


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(profile_id: UUID):
    async with get_session() as session:

        profile = await session.get(ProfileModel, profile_id)

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        await session.delete(profile)
        await session.commit()

        return None