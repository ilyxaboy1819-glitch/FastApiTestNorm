import json
import logging
from uuid import UUID
from typing import List

from src.repositories.application import ApplicationRepository
from src.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationRead
from src.exceptions import NotFoundException
from src.cache import get_cached, set_cached, delete_cached, delete_cached_pattern

logger = logging.getLogger(__name__)

CACHE_PREFIX = "application"


class ApplicationService:

    def __init__(self, repository: ApplicationRepository):
        self.repository = repository

    async def create(self, data: ApplicationCreate, user_id: UUID, category_id: UUID) -> ApplicationRead:
        app = data.to_model(user_id, category_id)
        app = await self.repository.create(app)
        logger.info(f"Application created with id={app.id}")
        await delete_cached_pattern(f"{CACHE_PREFIX}:list:*")
        return ApplicationRead.from_model(app)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ApplicationRead]:
        cache_key = f"{CACHE_PREFIX}:list:{skip}:{limit}"
        cached = await get_cached(cache_key)
        if cached:
            return [ApplicationRead.model_validate(a) for a in json.loads(cached)]

        logger.info(f"Getting applications skip={skip} limit={limit}")
        apps = await self.repository.get_all(skip, limit)
        result = ApplicationRead.from_list(apps)
        await set_cached(cache_key, json.dumps([a.model_dump(mode="json") for a in result]))
        return result

    async def get_by_id(self, app_id: UUID) -> ApplicationRead:
        cache_key = f"{CACHE_PREFIX}:{app_id}"
        cached = await get_cached(cache_key)
        if cached:
            return ApplicationRead.model_validate(json.loads(cached))

        app = await self.repository.get_by_id(app_id)
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")
        result = ApplicationRead.from_model(app)
        await set_cached(cache_key, json.dumps(result.model_dump(mode="json")))
        return result

    async def update(self, app_id: UUID, data: ApplicationUpdate, category_id: UUID) -> ApplicationRead:
        app = await self.repository.get_by_id(app_id)
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")

        fields = data.model_dump(exclude_unset=True)
        fields["category_id"] = category_id
        await self.repository.update(app_id, fields)
        logger.info(f"Application updated with id={app_id}")
        await delete_cached(f"{CACHE_PREFIX}:{app_id}")
        await delete_cached_pattern(f"{CACHE_PREFIX}:list:*")
        return await self.get_by_id(app_id)

    async def delete(self, app_id: UUID) -> None:
        app = await self.repository.get_by_id(app_id)
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")
        await self.repository.soft_delete(app_id)
        logger.info(f"Application soft deleted with id={app_id}")
        await delete_cached(f"{CACHE_PREFIX}:{app_id}")
        await delete_cached_pattern(f"{CACHE_PREFIX}:list:*")
