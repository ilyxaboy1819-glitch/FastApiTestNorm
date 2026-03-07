from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:123456@postgres:5432/postgres"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)