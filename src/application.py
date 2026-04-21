from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.exceptions import ValidationException
from src.exceptions.handler import validation_exception_handler
from src.healthcheck.router import router as healthcheck_router
from src.routers.user import router as user_router
from src.routers.application import router as application_router
from src.routers.role import router as role_router, category_router


def _setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ValidationException, validation_exception_handler)


def _setup_routers(app: FastAPI) -> None:
    app.include_router(healthcheck_router)
    app.include_router(user_router)
    app.include_router(application_router)
    app.include_router(role_router)
    app.include_router(category_router)


def get_app() -> FastAPI:
    app = FastAPI(
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=UJSONResponse,
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
