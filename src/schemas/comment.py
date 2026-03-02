from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    text: str | None = None


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