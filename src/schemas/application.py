from uuid import UUID
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class CategoryInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class ApplicationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class ApplicationCreate(ApplicationBase):
    user_id: UUID
    categories: List[CategoryInput] = Field(default_factory=list)


class ApplicationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    categories: Optional[List[CategoryInput]] = None


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