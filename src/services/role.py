import logging
from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.role import RoleModel
from src.schemas.role import RoleCreate, RoleUpdate, RoleRead
from src.exceptions import NotFoundException, AlreadyExistsException

logger = logging.getLogger(__name__)


class RoleService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_role_orm(self, role_id: UUID) -> RoleModel:
        result = await self.session.execute(
            sa.select(RoleModel)
            .options(selectinload(RoleModel.users))
            .where(RoleModel.id == role_id)
        )
        role = result.scalar_one_or_none()
        if not role:
            logger.warning(f"Role with id={role_id} not found")
            raise NotFoundException(f"Role with id={role_id} not found")
        return role

    async def create(self, data: RoleCreate) -> RoleRead:
        existing = await self.session.execute(
            sa.select(RoleModel).where(RoleModel.name == data.name)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Role with name='{data.name}' already exists")
            raise AlreadyExistsException("Role with this name already exists")

        role = RoleModel(**data.model_dump())
        role.users = []
        self.session.add(role)
        logger.info(f"Role created with id={role.id}")
        return RoleRead.model_validate(role)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[RoleRead]:
        logger.info(f"Getting roles skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(RoleModel)
            .options(selectinload(RoleModel.users))
            .offset(skip)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return [RoleRead.model_validate(r) for r in result.scalars().all()]

    async def get_by_id(self, role_id: UUID) -> RoleRead:
        role = await self._get_role_orm(role_id)
        return RoleRead.model_validate(role)

    async def update(self, role_id: UUID, data: RoleUpdate) -> RoleRead:
        role = await self._get_role_orm(role_id)

        if data.name != role.name:
            existing = await self.session.execute(
                sa.select(RoleModel).where(RoleModel.name == data.name)
            )
            if existing.scalar_one_or_none():
                logger.warning(f"Role with name='{data.name}' already exists")
                raise AlreadyExistsException("Role with this name already exists")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(role, field, value)

        logger.info(f"Role updated with id={role_id}")
        return RoleRead.model_validate(role)

    async def delete(self, role_id: UUID) -> None:
        role = await self._get_role_orm(role_id)
        await self.session.delete(role)
        logger.info(f"Role deleted with id={role_id}")
