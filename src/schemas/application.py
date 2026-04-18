from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, field_validator

from src.exceptions import ValidationException
from src.schemas.comment import CommentBase


class ApplicationBase(BaseModel):
    title: str
    description: Optional[str] = None

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="title", message="Title must not be empty")
        return v.strip()


class ApplicationCreate(ApplicationBase):
    user_id: UUID
    category_id: UUID
    comments: List[CommentBase] = []


class ApplicationUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: UUID

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="title", message="Title must not be empty")
        return v.strip()


class CommentShort(BaseModel):
    id: UUID
    text: str

    class Config:
        from_attributes = True


class ApplicationRead(ApplicationBase):
    id: UUID
    comments: List[CommentShort] = []

    class Config:
        from_attributes = True
