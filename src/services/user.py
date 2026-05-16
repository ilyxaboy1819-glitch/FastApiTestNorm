import json
import logging
from uuid import UUID
from typing import List

from src.repositories.user import UserRepository
from src.schemas.user import UserCreate, UserUpdate, UserRead
from src.exceptions import NotFoundException, AlreadyExistsException
from src.cache import get_cached, set_cached, delete_cached, delete_cached_pattern

logger = logging.getLogger(__name__)

CACHE_PREFIX = "user"


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create(self, data: UserCreate) -> UserRead:
        existing = await self.repository.get_by_username_or_email(data.username, data.email)
        if existing:
            logger.warning(f"User with username='{data.username}' or email='{data.email}' already exists")
            raise AlreadyExistsException("Username or email already exists")

        user = data.to_model()
        user = await self.repository.create(user)
        logger.info(f"User created with id={user.id}")
        await delete_cached_pattern(f"{CACHE_PREFIX}:list:*")
        return UserRead.from_model(user)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserRead]:
        cache_key = f"{CACHE_PREFIX}:list:{skip}:{limit}"
        cached = await get_cached(cache_key)
        if cached:
            return [UserRead.model_validate(u) for u in json.loads(cached)]

        logger.info(f"Getting users skip={skip} limit={limit}")
        users = await self.repository.get_all(skip, limit)
        result = UserRead.from_list(users)
        await set_cached(cache_key, json.dumps([u.model_dump(mode="json") for u in result]))
        return result

    async def get_by_id(self, user_id: UUID) -> UserRead:
        cache_key = f"{CACHE_PREFIX}:{user_id}"
        cached = await get_cached(cache_key)
        if cached:
            return UserRead.model_validate(json.loads(cached))

        user = await self.repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User with id={user_id} not found")
            raise NotFoundException(f"User with id={user_id} not found")
        result = UserRead.from_model(user)
        await set_cached(cache_key, json.dumps(result.model_dump(mode="json")))
        return result

    async def update(self, user_id: UUID, data: UserUpdate) -> UserRead:
        user = await self.repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User with id={user_id} not found")
            raise NotFoundException(f"User with id={user_id} not found")

        self._update_fields(user, data.model_dump(exclude_unset=True, exclude={"profile"}))

        if data.profile is not None:
            self._update_fields(user.profile, data.profile.model_dump(exclude_unset=True))

        await self.repository.update(user)
        logger.info(f"User updated with id={user_id}")
        await delete_cached(f"{CACHE_PREFIX}:{user_id}")
        await delete_cached_pattern(f"{CACHE_PREFIX}:list:*")
        return UserRead.from_model(user)

    async def delete(self, user_id: UUID) -> None:
        user = await self.repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User with id={user_id} not found")
            raise NotFoundException(f"User with id={user_id} not found")
        await self.repository.soft_delete(user)
        logger.info(f"User deleted with id={user_id}")
        await delete_cached(f"{CACHE_PREFIX}:{user_id}")
        await delete_cached_pattern(f"{CACHE_PREFIX}:list:*")

    @staticmethod
    def _update_fields(obj, fields: dict) -> None:
        for field, value in fields.items():
            setattr(obj, field, value)
