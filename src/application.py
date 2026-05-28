import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.exceptions import ValidationException, NotFoundException, AlreadyExistsException
from src.exceptions.handler import (
    validation_exception_handler,
    not_found_exception_handler,
    already_exists_exception_handler,
)
from src.healthcheck.router import router as healthcheck_router
from src.routers.user import router as user_router
from src.routers.application import router as application_router
from src.routers.role import router as role_router
from src.routers.order import router as order_router
from src.workers.order_worker import order_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    order_task = asyncio.create_task(order_worker())
    yield
    order_task.cancel()


def _setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
    app.add_exception_handler(AlreadyExistsException, already_exists_exception_handler)


def _setup_routers(app: FastAPI) -> None:
    app.include_router(healthcheck_router)
    app.include_router(user_router)
    app.include_router(application_router)
    app.include_router(role_router)
    app.include_router(order_router)


def get_app() -> FastAPI:
    app = FastAPI(
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=JSONResponse,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _setup_exception_handlers(app)
    _setup_routers(app)

    return app


app = get_app()
