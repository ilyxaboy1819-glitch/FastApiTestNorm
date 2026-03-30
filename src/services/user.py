import logging
from uuid import UUID
from typing import List
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import UserModel
from src.models.profile import ProfileModel
from src.schemas.user import UserCreate, UserUpdate, UserRead
from src.schemas.profile import ProfileCreate, ProfileBase, ProfileRead
from src.exceptions import NotFoundException, AlreadyExistsException

logger = logging.getLogger(__name__)


class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_user_orm(self, user_id: UUID) -> UserModel:
        result = await self.session.execute(
            sa.select(UserModel)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.roles),
            )
            .where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"User with id={user_id} not found")
            raise NotFoundException(f"User with id={user_id} not found")
        return user

    async def create(self, data: UserCreate) -> UserRead:
        existing = await self.session.execute(
            sa.select(UserModel).where(
                (UserModel.username == data.username) |
                (UserModel.email == data.email)
            )
        )
        if existing.scalar_one_or_none():
            logger.warning(f"User with username='{data.username}' or email='{data.email}' already exists")
            raise AlreadyExistsException("Username or email already exists")

        user = UserModel(**data.model_dump())
        user.roles = []
        user.profile = None
        self.session.add(user)
        logger.info(f"User created with id={user.id}")
        return UserRead.model_validate(user)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserRead]:
        logger.info(f"Getting users skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(UserModel)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.roles),
            )
            .offset(skip)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return [UserRead.model_validate(u) for u in result.scalars().all()]

    async def get_by_id(self, user_id: UUID) -> UserRead:
        user = await self._get_user_orm(user_id)
        return UserRead.model_validate(user)

    async def update(self, user_id: UUID, data: UserUpdate) -> UserRead:
        user = await self._get_user_orm(user_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        logger.info(f"User updated with id={user_id}")
        return UserRead.model_validate(user)

    async def delete(self, user_id: UUID) -> None:
        user = await self._get_user_orm(user_id)
        await self.session.delete(user)
        logger.info(f"User deleted with id={user_id}")

    async def create_profile(self, data: ProfileCreate) -> ProfileRead:
        user = await self.session.get(UserModel, data.user_id)
        if not user:
            logger.warning(f"User with id={data.user_id} not found")
            raise NotFoundException(f"User with id={data.user_id} not found")

        existing = await self.session.execute(
            sa.select(ProfileModel).where(ProfileModel.user_id == data.user_id)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Profile for user_id={data.user_id} already exists")
            raise AlreadyExistsException("Profile for this user already exists")

        profile = ProfileModel(**data.model_dump())
        profile.user = user
        self.session.add(profile)
        logger.info(f"Profile created with id={profile.id}")
        return ProfileRead.model_validate(profile)

    async def get_all_profiles(self, skip: int = 0, limit: int = 100) -> List[ProfileRead]:
        logger.info(f"Getting profiles skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(ProfileModel)
            .options(selectinload(ProfileModel.user))
            .offset(skip)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return [ProfileRead.model_validate(p) for p in result.scalars().all()]

    async def get_profile_by_id(self, profile_id: UUID) -> ProfileRead:
        result = await self.session.execute(
            sa.select(ProfileModel)
            .options(selectinload(ProfileModel.user))
            .where(ProfileModel.id == profile_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            logger.warning(f"Profile with id={profile_id} not found")
            raise NotFoundException(f"Profile with id={profile_id} not found")
        return ProfileRead.model_validate(profile)

    async def update_profile(self, profile_id: UUID, data: ProfileBase) -> ProfileRead:
        result = await self.session.execute(
            sa.select(ProfileModel)
            .options(selectinload(ProfileModel.user))
            .where(ProfileModel.id == profile_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            logger.warning(f"Profile with id={profile_id} not found")
            raise NotFoundException(f"Profile with id={profile_id} not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)

        logger.info(f"Profile updated with id={profile_id}")
        return ProfileRead.model_validate(profile)

    async def delete_profile(self, profile_id: UUID) -> None:
        profile = await self.session.get(ProfileModel, profile_id)
        if not profile:
            logger.warning(f"Profile with id={profile_id} not found")
            raise NotFoundException(f"Profile with id={profile_id} not found")
        await self.session.delete(profile)
        logger.info(f"Profile deleted with id={profile_id}")
