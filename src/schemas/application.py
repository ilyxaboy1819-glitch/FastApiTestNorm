from uuid import UUID
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_validator


class CategoryInput(BaseModel):
    id: UUID


class ApplicationBase(BaseModel):
    title: str
    description: Optional[str] = None

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title must not be empty')
        return v.strip()


class ApplicationCreate(ApplicationBase):
    user_id: UUID
    categories: List[CategoryInput] = []


class ApplicationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[List[CategoryInput]] = None

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Title must not be empty')
        return v.strip() if v else v


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
    updated_at: Optional[datetime] = None

    user_id: UUID
    categories: List[CategoryShort] = []
    comments: List[CommentShort] = []

    class Config:
        from_attributes = True