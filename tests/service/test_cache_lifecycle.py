import src.cache as cache_module
from src.schemas.user import UserCreate, UserUpdate
from src.schemas.profile import ProfileBase
from src.services.user import UserService


class TestUserCacheLifecycle:

    async def test_get_by_id_cache_miss_then_hit(self, user_service: UserService, test_redis, monkeypatch):
        monkeypatch.setattr(cache_module, "redis_client", test_redis)

        data = UserCreate(
            username="cacheuser1",
            email="cache1@example.com",
            profile=ProfileBase(bio="bio"),
        )
        created = await user_service.create(data)

        result1 = await user_service.get_by_id(created.id)
        assert result1.username == "cacheuser1"

        cached_value = await test_redis.get(f"user:{created.id}")
        assert cached_value is not None

        result2 = await user_service.get_by_id(created.id)
        assert result2.username == "cacheuser1"
        assert result2.id == result1.id

    async def test_update_invalidates_cache(self, user_service: UserService, test_redis, monkeypatch):
        monkeypatch.setattr(cache_module, "redis_client", test_redis)

        data = UserCreate(
            username="cacheuser2",
            email="cache2@example.com",
            profile=ProfileBase(bio="bio"),
        )
        created = await user_service.create(data)

        await user_service.get_by_id(created.id)
        cached_before = await test_redis.get(f"user:{created.id}")
        assert cached_before is not None

        update_data = UserUpdate(
            username="cacheuser2_updated",
            email="cache2@example.com",
        )
        await user_service.update(created.id, update_data)

        cached_after = await test_redis.get(f"user:{created.id}")
        assert cached_after is None

        result = await user_service.get_by_id(created.id)
        assert result.username == "cacheuser2_updated"

        cached_final = await test_redis.get(f"user:{created.id}")
        assert cached_final is not None

    async def test_delete_invalidates_cache(self, user_service: UserService, test_redis, monkeypatch):
        monkeypatch.setattr(cache_module, "redis_client", test_redis)

        data = UserCreate(
            username="cacheuser3",
            email="cache3@example.com",
            profile=ProfileBase(bio="bio"),
        )
        created = await user_service.create(data)

        await user_service.get_by_id(created.id)
        cached = await test_redis.get(f"user:{created.id}")
        assert cached is not None

        await user_service.delete(created.id)

        cached_after = await test_redis.get(f"user:{created.id}")
        assert cached_after is None

    async def test_list_cache_invalidated_on_create(self, user_service: UserService, test_redis, monkeypatch):
        monkeypatch.setattr(cache_module, "redis_client", test_redis)

        await user_service.get_all(skip=0, limit=100)
        list_cached = await test_redis.get("user:list:0:100")
        assert list_cached is not None

        data = UserCreate(
            username="cacheuser4",
            email="cache4@example.com",
            profile=ProfileBase(bio="bio"),
        )
        await user_service.create(data)

        list_cached_after = await test_redis.get("user:list:0:100")
        assert list_cached_after is None
