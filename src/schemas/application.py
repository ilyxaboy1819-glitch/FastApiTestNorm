from uuid import UUID
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ApplicationBase(BaseModel):
    title: str
    description: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    categories: List[str] = Field(default_factory=list)


class ApplicationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[List[str]] = None


class UserShort(BaseModel):
    id: UUID
    username: str

    class Config:
        from_attributes = True


class CategoryShort(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class CommentShort(BaseModel):
    id: UUID
    text: str

    class Config:
        from_attributes = True


class ApplicationRead(ApplicationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    user: UserShort
    categories: List[CategoryShort] = Field(default_factory=list)
    comments: List[CommentShort] = Field(default_factory=list)

    class Config:
        from_attributes = True