import logging
from uuid import UUID
from typing import List
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import UserModel
from src.models.profile import ProfileModel
from src.schemas.user import UserCreate, UserUpdate, UserRead
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

        user = UserModel(**data.model_dump(exclude={"profile"}))
        self.session.add(user)
        await self.session.flush()

        profile = ProfileModel(**data.profile.model_dump(), user_id=user.id)
        self.session.add(profile)

        await self.session.flush()
        logger.info(f"User created with id={user.id}")
        await self.session.refresh(user, ["profile", "roles"])
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
        )
        return [UserRead.model_validate(u) for u in result.scalars().all()]

    async def get_by_id(self, user_id: UUID) -> UserRead:
        user = await self._get_user_orm(user_id)
        return UserRead.model_validate(user)

    async def update(self, user_id: UUID, data: UserUpdate) -> UserRead:
        user = await self._get_user_orm(user_id)

        self._update_fields(user, data.model_dump(exclude_unset=True, exclude={"profile"}))

        if data.profile is not None:
            self._update_fields(user.profile, data.profile.model_dump(exclude_unset=True))

        logger.info(f"User updated with id={user_id}")
        return UserRead.model_validate(user)

    async def delete(self, user_id: UUID) -> None:
        user = await self._get_user_orm(user_id)
        await self.session.delete(user)
        logger.info(f"User deleted with id={user_id}")

    @staticmethod
    def _update_fields(obj, fields: dict) -> None:
        for field, value in fields.items():
            setattr(obj, field, value)
