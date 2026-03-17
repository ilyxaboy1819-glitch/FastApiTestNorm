from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator


class CommentBase(BaseModel):
    text: str

    @field_validator('text')
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Text must not be empty')
        return v.strip()


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    text: Optional[str] = None

    @field_validator('text')
    @classmethod
    def text_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Text must not be empty')
        return v.strip() if v else v


class ApplicationShort(BaseModel):
    id: UUID
    title: str

    class Config:
        from_attributes = True


class CommentRead(CommentBase):
    id: UUID
    created_at: datetime
    application: ApplicationShort

    class Config:
        from_attributes = True