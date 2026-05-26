import logging
from uuid import UUID
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.role import RoleModel

logger = logging.getLogger(__name__)


class RoleRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, role: RoleModel) -> RoleModel:
        self.session.add(role)
        await self.session.flush()
        await self.session.refresh(role, ["users"])
        return role

    async def get_by_id(self, role_id: UUID) -> Optional[RoleModel]:
        result = await self.session.execute(
            sa.select(RoleModel)
            .options(selectinload(RoleModel.users))
            .where(RoleModel.id == role_id, RoleModel.is_deleted == False)
            .with_for_update(skip_locked=True)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[RoleModel]:
        result = await self.session.execute(
            sa.select(RoleModel)
            .options(selectinload(RoleModel.users))
            .where(RoleModel.is_deleted == False)
            .with_for_update(skip_locked=True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Optional[RoleModel]:
        result = await self.session.execute(
            sa.select(RoleModel).where(RoleModel.name == name)
        )
        return result.scalar_one_or_none()

    async def update(self, role: RoleModel) -> None:
        await self.session.flush()

    async def soft_delete(self, role: RoleModel) -> None:
        role.is_deleted = True
        await self.session.flush()
