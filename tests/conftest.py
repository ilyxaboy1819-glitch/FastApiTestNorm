import pytest
import pytest_asyncio
from typing import AsyncGenerator

from alembic import command
from alembic.config import Config
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from httpx import AsyncClient, ASGITransport

import src.cache as cache_module
from src.application import get_app
from src.db import get_session
from src.repositories.user import UserRepository
from src.repositories.role import RoleRepository
from src.repositories.application import ApplicationRepository
from src.services.user import UserService
from src.services.role import RoleService
from src.services.application import ApplicationService


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:14") as pg:
        yield pg


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest.fixture(scope="session")
def db_url(postgres_container) -> str:
    return postgres_container.get_connection_url().replace("psycopg2", "asyncpg")


@pytest.fixture(scope="session")
def _run_migrations(db_url):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")


@pytest_asyncio.fixture(scope="session")
async def async_engine(db_url, _run_migrations) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(db_url, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture
async def session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_redis(redis_container) -> AsyncGenerator[Redis, None]:
    redis_url = f"redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}/0"
    test_redis = Redis.from_url(redis_url, decode_responses=True)
    yield test_redis
    await test_redis.flushdb()
    await test_redis.aclose()


@pytest.fixture
def user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


@pytest.fixture
def role_repository(session: AsyncSession) -> RoleRepository:
    return RoleRepository(session)


@pytest.fixture
def application_repository(session: AsyncSession) -> ApplicationRepository:
    return ApplicationRepository(session)


@pytest.fixture
def user_service(user_repository: UserRepository) -> UserService:
    return UserService(user_repository)


@pytest.fixture
def role_service(role_repository: RoleRepository) -> RoleService:
    return RoleService(role_repository)


@pytest.fixture
def application_service(application_repository: ApplicationRepository) -> ApplicationService:
    return ApplicationService(application_repository)


@pytest.fixture
async def client(session: AsyncSession, test_redis, monkeypatch) -> AsyncGenerator[AsyncClient, None]:
    monkeypatch.setattr(cache_module, "redis_client", test_redis)

    app = get_app()

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
