
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class ApplicationShort(BaseModel):
    id: UUID
    title: str

    class Config:
        from_attributes = True


class CategoryRead(CategoryBase):
    id: UUID
    applications: List[ApplicationShort] = Field(default_factory=list)

    class Config:
        from_attributes = True