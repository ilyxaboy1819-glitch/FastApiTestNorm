from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    text: str | None = Field(None, min_length=1, max_length=2000)


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