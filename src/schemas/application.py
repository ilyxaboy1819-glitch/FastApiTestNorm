from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, field_validator, Field

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

    @field_validator('description')
    @classmethod
    def description_must_not_be_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValidationException(field="description", message="Description must not be empty if provided")
        return v.strip() if v else v


class ApplicationCreate(ApplicationBase):
    user_id: UUID
    category_id: UUID
    comments: List[CommentBase] = Field(default=[])

    @field_validator('comments')
    @classmethod
    def comments_must_not_be_empty(cls, v: List[CommentBase]) -> List[CommentBase]:
        if not v:
            raise ValidationException(field="comments", message="Comments must not be empty")
        return v


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

    @field_validator('description')
    @classmethod
    def description_must_not_be_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValidationException(field="description", message="Description must not be empty if provided")
        return v.strip() if v else v


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
