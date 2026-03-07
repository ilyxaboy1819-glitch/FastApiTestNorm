from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
)
from contextlib import asynccontextmanager

from .dependency import engine

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

@asynccontextmanager
async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session