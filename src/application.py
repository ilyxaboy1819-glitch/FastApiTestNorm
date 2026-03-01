from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.healthcheck.router import router as healthcheck_router
from src.routers.user import router as user_router
from src.routers.application import router as application_router
from src.routers.category import router as category_router
from src.routers.profile import router as profile_router
from src.routers.role import router as role_router
from src.routers.comment import router as comment_router


def get_app(lifespan=None) -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.
    """

    app = FastAPI(
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=UJSONResponse,
        lifespan=lifespan,   # ← ВОТ ЭТА СТРОКА НОВАЯ
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(healthcheck_router)
    app.include_router(user_router)
    app.include_router(application_router)
    app.include_router(category_router)
    app.include_router(profile_router)
    app.include_router(role_router)
    app.include_router(comment_router)

    return app