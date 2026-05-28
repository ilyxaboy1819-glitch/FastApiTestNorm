import json
import logging
from uuid import UUID
from typing import List

from src.models.role import RoleModel
from src.repositories.role import RoleRepository
from src.schemas.role import RoleCreate, RoleUpdate, RoleRead
from src.exceptions import NotFoundException, AlreadyExistsException
from src.cache import get_cached, set_cached, delete_cached, delete_cached_pattern

logger = logging.getLogger(__name__)

CACHE_PREFIX = "role"


class RoleService:

    def __init__(self, repository: RoleRepository):
        self.repository = repository

    async def create(self, data: RoleCreate) -> RoleRead:
        existing = await self.repository.get_by_name(data.name)
        if existing:
            logger.warning(f"Role with name='{data.name}' already exists")
            raise AlreadyExistsException("Role with this name already exists")

        role = RoleModel(**data.model_dump())
        role = await self.repository.create(role)
        logger.info(f"Role created with id={role.id}")
        await delete_cached_pattern(f"{CACHE_PREFIX}:list:*")
        return RoleRead.from_model(role)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[RoleRead]:
        cache_key = f"{CACHE_PREFIX}:list:{skip}:{limit}"
        cached = await get_cached(cache_key)
        if cached:
            return [RoleRead.model_validate(r) for r in json.loads(cached)]

        logger.info(f"Getting roles skip={skip} limit={limit}")
        roles = await self.repository.get_all(skip, limit)
        result = RoleRead.from_list(roles)
        await set_cached(cache_key, json.dumps([r.model_dump(mode="json") for r in result]))
        return result

    async def get_by_id(self, role_id: UUID) -> RoleRead:
        cache_key = f"{CACHE_PREFIX}:{role_id}"
        cached = await get_cached(cache_key)
        if cached:
            return RoleRead.model_validate(json.loads(cached))

        role = await self.repository.get_by_id(role_id)
        if not role:
            logger.warning(f"Role with id={role_id} not found")
            raise NotFoundException(f"Role with id={role_id} not found")
        result = RoleRead.from_model(role)
        await set_cached(cache_key, json.dumps(result.model_dump(mode="json")))
        return result

    async def update(self, role_id: UUID, data: RoleUpdate) -> RoleRead:
        existing = await self.repository.get_by_name(data.name)
        if existing:
            logger.warning(f"Role with name='{data.name}' already exists")
            raise AlreadyExistsException("Role with this name already exists")

        role = await self.repository.get_by_id(role_id)
        if not role:
            logger.warning(f"Role with id={role_id} not found")
            raise NotFoundException(f"Role with id={role_id} not found")

        self._update_fields(role, data.model_dump(exclude_unset=True))
        await self.repository.update(role)
        logger.info(f"Role updated with id={role_id}")
        await delete_cached(f"{CACHE_PREFIX}:{role_id}")
        await delete_cached_pattern(f"{CACHE_PREFIX}:list:*")
        return RoleRead.from_model(role)

    async def delete(self, role_id: UUID) -> None:
        role = await self.repository.get_by_id(role_id)
        if not role:
            logger.warning(f"Role with id={role_id} not found")
            raise NotFoundException(f"Role with id={role_id} not found")
        await self.repository.soft_delete(role)
        logger.info(f"Role deleted with id={role_id}")
        await delete_cached(f"{CACHE_PREFIX}:{role_id}")
        await delete_cached_pattern(f"{CACHE_PREFIX}:list:*")

    @staticmethod
    def _update_fields(obj, fields: dict) -> None:
        for field, value in fields.items():
            setattr(obj, field, value)
