import logging
from typing import Optional

from redis.asyncio import Redis

from src.config import Settings

logger = logging.getLogger(__name__)

settings = Settings()

CACHE_TTL = 3600

redis_client: Redis = Redis.from_url(settings.redis_url, decode_responses=True)


async def get_cached(key: str) -> Optional[str]:
    value = await redis_client.get(key)
    if value:
        logger.debug(f"Cache hit: {key}")
    return value


async def set_cached(key: str, value: str, ttl: int = CACHE_TTL) -> None:
    await redis_client.set(key, value, ex=ttl)
    logger.debug(f"Cache set: {key} (ttl={ttl})")


async def delete_cached(key: str) -> None:
    await redis_client.delete(key)
    logger.debug(f"Cache deleted: {key}")


async def delete_cached_pattern(pattern: str) -> None:
    keys = []
    async for key in redis_client.scan_iter(match=pattern):
        keys.append(key)
    if keys:
        await redis_client.delete(*keys)
        logger.debug(f"Cache invalidated {len(keys)} keys matching: {pattern}")
