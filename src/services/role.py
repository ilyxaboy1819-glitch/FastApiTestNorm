import logging
from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.role import RoleModel
from src.schemas.role import RoleCreate, RoleUpdate
from src.exceptions import NotFoundException, AlreadyExistsException

logger = logging.getLogger(__name__)


class RoleService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_with_relations(self, role_id: UUID) -> RoleModel:
        result = await self.session.execute(
            sa.select(RoleModel)
            .options(selectinload(RoleModel.users))
            .where(RoleModel.id == role_id)
        )
        return result.scalar_one()

    async def create(self, data: RoleCreate) -> RoleModel:
        existing = await self.session.execute(
            sa.select(RoleModel).where(RoleModel.name == data.name)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Role with name='{data.name}' already exists")
            raise AlreadyExistsException("Role with this name already exists")

        role = RoleModel(**data.model_dump())
        self.session.add(role)
        await self.session.flush()
        logger.info(f"Role created with id={role.id}")
        return await self._get_with_relations(role.id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[RoleModel]:
        logger.info(f"Getting roles skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(RoleModel)
            .options(selectinload(RoleModel.users))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, role_id: UUID) -> RoleModel:
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

    async def update(self, role_id: UUID, data: RoleUpdate) -> RoleModel:
        role = await self.session.get(RoleModel, role_id)
        if not role:
            logger.warning(f"Role with id={role_id} not found")
            raise NotFoundException(f"Role with id={role_id} not found")

        if data.name and data.name != role.name:
            existing = await self.session.execute(
                sa.select(RoleModel).where(RoleModel.name == data.name)
            )
            if existing.scalar_one_or_none():
                logger.warning(f"Role with name='{data.name}' already exists")
                raise AlreadyExistsException("Role with this name already exists")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(role, field, value)

        await self.session.flush()
        logger.info(f"Role updated with id={role_id}")
        return await self._get_with_relations(role_id)

    async def delete(self, role_id: UUID) -> None:
        role = await self.session.get(RoleModel, role_id)
        if not role:
            logger.warning(f"Role with id={role_id} not found")
            raise NotFoundException(f"Role with id={role_id} not found")
        await self.session.delete(role)
        logger.info(f"Role deleted with id={role_id}")