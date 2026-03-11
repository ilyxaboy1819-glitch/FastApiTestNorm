from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.profile import ProfileModel
from src.schemas.profile import ProfileCreate, ProfileUpdate
from src.exceptions import NotFoundException, AlreadyExistsException


class ProfileService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ProfileCreate) -> ProfileModel:
        existing = await self.session.execute(
            sa.select(ProfileModel).where(ProfileModel.user_id == data.user_id)
        )
        if existing.scalar_one_or_none():
            raise AlreadyExistsException("Profile for this user already exists")

        profile = ProfileModel(**data.model_dump())
        self.session.add(profile)
        await self.session.flush()
        await self.session.refresh(profile)
        return profile

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ProfileModel]:
        result = await self.session.execute(
            sa.select(ProfileModel).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, profile_id: UUID) -> ProfileModel:
        profile = await self.session.get(ProfileModel, profile_id)
        if not profile:
            raise NotFoundException("Profile not found")
        return profile

    async def update(self, profile_id: UUID, data: ProfileUpdate) -> ProfileModel:
        profile = await self.session.get(ProfileModel, profile_id)
        if not profile:
            raise NotFoundException("Profile not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)

        await self.session.flush()
        await self.session.refresh(profile)
        return profile

    async def delete(self, profile_id: UUID) -> None:
        profile = await self.session.get(ProfileModel, profile_id)
        if not profile:
            raise NotFoundException("Profile not found")
        await self.session.delete(profile)