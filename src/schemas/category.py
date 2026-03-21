from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, field_validator

from src.exceptions import ValidationException


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="name", message="Name must not be empty")
        return v.strip()


class CategoryUpdate(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="name", message="Name must not be empty")
        return v.strip()


class ApplicationShort(BaseModel):
    id: UUID
    title: str

    class Config:
        from_attributes = True


class CategoryRead(CategoryBase):
    id: UUID
    applications: List[ApplicationShort] = []

    class Config:
        from_attributes = True