from uuid import UUID
from pydantic import BaseModel, field_validator

from src.exceptions import ValidationException


class CommentBase(BaseModel):
    text: str

    @field_validator('text')
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="text", message="Text must not be empty")
        return v.strip()


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    id: UUID
    application_id: UUID

    class Config:
        from_attributes = True