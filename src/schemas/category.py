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

    @field_validator('description')
    @classmethod
    def description_must_not_be_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValidationException(field="description", message="Description must not be empty if provided")
        return v.strip() if v else v


class CategoryUpdate(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="name", message="Name must not be empty")
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_must_not_be_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValidationException(field="description", message="Description must not be empty")
        return v.strip() if v else v


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