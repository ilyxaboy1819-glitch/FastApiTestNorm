from fastapi import FastAPI, Request
from fastapi.responses import UJSONResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.exceptions import ValidationException
from src.healthcheck.router import router as healthcheck_router
from src.routers.user import router as user_router
from src.routers.application import router as application_router
from src.routers.role import router as role_router


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

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException):
        return JSONResponse(
            status_code=422,
            content={"error": exc.message, "field": exc.field},
        )

    app.include_router(healthcheck_router)
    app.include_router(user_router)
    app.include_router(application_router)
    app.include_router(role_router)

    return app


app = get_app()