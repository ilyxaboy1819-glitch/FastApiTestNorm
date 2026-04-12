from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import UJSONResponse

from src.exceptions import ValidationException


async def validation_exception_handler(request: Request, exc: ValidationException) -> UJSONResponse:
    return UJSONResponse(
        status_code=422,
        content={"error": exc.message, "field": exc.field},
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> UJSONResponse:
    errors = exc.errors()
    field = errors[0]["loc"][-1] if errors else "unknown"
    message = errors[0]["msg"] if errors else "Validation error"
    return UJSONResponse(
        status_code=422,
        content={"error": message, "field": field},
    )
