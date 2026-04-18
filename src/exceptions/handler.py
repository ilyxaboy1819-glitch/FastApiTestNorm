from http import HTTPStatus

from fastapi import Request
from fastapi.responses import UJSONResponse

from src.exceptions import ValidationException
from src.schemas.error import ValidationErrorResponse


async def validation_exception_handler(request: Request, exc: ValidationException) -> UJSONResponse:
    body = ValidationErrorResponse(error=exc.message, field=exc.field)
    return UJSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content=body.model_dump(),
    )
