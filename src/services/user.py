from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import UserModel
from src.schemas.user import UserCreate, UserUpdate
from src.exceptions import NotFoundException, AlreadyExistsException


class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_with_relations(self, user_id: UUID) -> UserModel:
        result = await self.session.execute(
            sa.select(UserModel)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.roles),
            )
            .where(UserModel.id == user_id)
        )
        return result.scalar_one()

    async def create(self, data: UserCreate) -> UserModel:
        existing = await self.session.execute(
            sa.select(UserModel).where(
                (UserModel.username == data.username) |
                (UserModel.email == data.email)
            )
        )
        if existing.scalar_one_or_none():
            raise AlreadyExistsException("Username or email already exists")

        user = UserModel(**data.model_dump())
        self.session.add(user)
        await self.session.flush()
        return await self._get_with_relations(user.id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        result = await self.session.execute(
            sa.select(UserModel)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.roles),
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, user_id: UUID) -> UserModel:
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
            raise NotFoundException("User not found")
        return user

    async def update(self, user_id: UUID, data: UserUpdate) -> UserModel:
        user = await self.session.get(UserModel, user_id)
        if not user:
            raise NotFoundException("User not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        await self.session.flush()
        return await self._get_with_relations(user_id)

    async def delete(self, user_id: UUID) -> None:
        user = await self.session.get(UserModel, user_id)
        if not user:
            raise NotFoundException("User not found")
        await self.session.delete(user)