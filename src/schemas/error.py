from typing import Optional
from pydantic import BaseModel


class ValidationErrorResponse(BaseModel):
    error: str
    field: str


class NotFoundErrorResponse(BaseModel):
    error: str


class InternalErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
