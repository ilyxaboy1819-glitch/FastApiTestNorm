import uvicorn
from contextlib import asynccontextmanager

from src.application import get_app
from src.db import engine
from src.db.base import Base
import src.models

@asynccontextmanager
async def lifespan(app):
    print("🚀 Creating database tables...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    print("🛑 Shutdown")


app = get_app(lifespan=lifespan)


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)