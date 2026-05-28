from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse

from src.exceptions import ValidationException, NotFoundException, AlreadyExistsException
from src.schemas.error import ValidationErrorResponse


async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    body = ValidationErrorResponse(error=exc.message, field=exc.field)
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content=body.model_dump(),
    )


async def not_found_exception_handler(request: Request, exc: NotFoundException) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"detail": exc.detail},
    )


async def already_exists_exception_handler(request: Request, exc: AlreadyExistsException) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.CONFLICT,
        content={"detail": exc.detail},
    )
