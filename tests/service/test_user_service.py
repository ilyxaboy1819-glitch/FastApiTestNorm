import pytest
from uuid import uuid4

import src.cache as cache_module
from src.schemas.user import UserCreate, UserUpdate
from src.schemas.profile import ProfileBase
from src.services.user import UserService
from src.exceptions import NotFoundException, AlreadyExistsException


def _unique_user(prefix: str = "user") -> UserCreate:
    uid = uuid4().hex[:8]
    return UserCreate(
        username=f"{prefix}_{uid}",
        email=f"{prefix}_{uid}@example.com",
        profile=ProfileBase(bio="test bio"),
    )


@pytest.fixture(autouse=True)
def _patch_redis(test_redis, monkeypatch):
    monkeypatch.setattr(cache_module, "redis_client", test_redis)


class TestUserServiceCreate:

    async def test_create_success(self, user_service: UserService):
        data = _unique_user("create")
        result = await user_service.create(data)

        assert result.username == data.username
        assert result.email == data.email
        assert result.profile is not None
        assert result.id is not None

    async def test_create_duplicate_username(self, user_service: UserService):
        uid = uuid4().hex[:8]
        data = UserCreate(
            username=f"dup_{uid}",
            email=f"dup1_{uid}@example.com",
            profile=ProfileBase(bio="bio"),
        )
        await user_service.create(data)

        data2 = UserCreate(
            username=f"dup_{uid}",
            email=f"dup2_{uid}@example.com",
            profile=ProfileBase(bio="bio"),
        )
        with pytest.raises(AlreadyExistsException):
            await user_service.create(data2)

    async def test_create_duplicate_email(self, user_service: UserService):
        uid = uuid4().hex[:8]
        data = UserCreate(
            username=f"email1_{uid}",
            email=f"same_{uid}@example.com",
            profile=ProfileBase(bio="bio"),
        )
        await user_service.create(data)

        data2 = UserCreate(
            username=f"email2_{uid}",
            email=f"same_{uid}@example.com",
            profile=ProfileBase(bio="bio"),
        )
        with pytest.raises(AlreadyExistsException):
            await user_service.create(data2)


class TestUserServiceGetById:

    async def test_get_by_id_success(self, user_service: UserService):
        data = _unique_user("getuser")
        created = await user_service.create(data)

        result = await user_service.get_by_id(created.id)
        assert result.username == data.username
        assert result.id == created.id

    async def test_get_by_id_not_found(self, user_service: UserService):
        with pytest.raises(NotFoundException):
            await user_service.get_by_id(uuid4())


class TestUserServiceDelete:

    async def test_delete_success(self, user_service: UserService):
        data = _unique_user("deluser")
        created = await user_service.create(data)

        await user_service.delete(created.id)

        with pytest.raises(NotFoundException):
            await user_service.get_by_id(created.id)

    async def test_delete_not_found(self, user_service: UserService):
        with pytest.raises(NotFoundException):
            await user_service.delete(uuid4())
