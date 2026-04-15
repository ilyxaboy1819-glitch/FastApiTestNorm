from http import HTTPStatus

from fastapi import Request
from fastapi.responses import UJSONResponse

from src.exceptions import ValidationException


async def validation_exception_handler(request: Request, exc: ValidationException) -> UJSONResponse:
    return UJSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"error": exc.message, "field": exc.field},
    )
