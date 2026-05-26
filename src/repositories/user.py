import logging
from uuid import UUID
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import UserModel

logger = logging.getLogger(__name__)


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserModel) -> UserModel:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user, ["profile", "roles"])
        return user

    async def get_by_id(self, user_id: UUID) -> Optional[UserModel]:
        result = await self.session.execute(
            sa.select(UserModel)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.roles),
            )
            .where(UserModel.id == user_id, UserModel.is_deleted == False)
            .with_for_update(skip_locked=True)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        result = await self.session.execute(
            sa.select(UserModel)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.roles),
            )
            .where(UserModel.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_username_or_email(self, username: str, email: str) -> Optional[UserModel]:
        result = await self.session.execute(
            sa.select(UserModel).where(
                (UserModel.username == username) | (UserModel.email == email)
            )
        )
        return result.scalar_one_or_none()

    async def update(self, user: UserModel) -> None:
        await self.session.flush()

    async def soft_delete(self, user: UserModel) -> None:
        user.is_deleted = True
        await self.session.flush()
