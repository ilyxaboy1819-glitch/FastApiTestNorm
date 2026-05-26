import logging
from typing import Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

CACHE_TTL = 3600

redis_client: Redis = Redis.from_url(settings.redis_url, decode_responses=True)

_redis_retry = retry(
    retry=retry_if_exception_type(RedisError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.1, max=0.5),
    reraise=True,
)


async def get_cached(key: str) -> Optional[str]:
    try:
        value = await _redis_retry(redis_client.get)(key)
        if value:
            logger.debug(f"Cache hit: {key}")
        return value
    except RedisError as e:
        logger.warning(f"Redis unavailable on get({key}): {e}")
        return None


async def set_cached(key: str, value: str, ttl: int = CACHE_TTL) -> None:
    try:
        await _redis_retry(redis_client.set)(key, value, ex=ttl)
        logger.debug(f"Cache set: {key} (ttl={ttl})")
    except RedisError as e:
        logger.warning(f"Redis unavailable on set({key}): {e}")


async def delete_cached(key: str) -> None:
    try:
        await _redis_retry(redis_client.delete)(key)
        logger.debug(f"Cache deleted: {key}")
    except RedisError as e:
        logger.warning(f"Redis unavailable on delete({key}): {e}")


async def delete_cached_pattern(pattern: str) -> None:
    try:
        keys = []
        async for key in redis_client.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await _redis_retry(redis_client.delete)(*keys)
            logger.debug(f"Cache invalidated {len(keys)} keys matching: {pattern}")
    except RedisError as e:
        logger.warning(f"Redis unavailable on delete_pattern({pattern}): {e}")
