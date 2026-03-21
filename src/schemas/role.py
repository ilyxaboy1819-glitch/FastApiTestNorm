from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, field_validator

from src.exceptions import ValidationException


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="name", message="Name must not be empty")
        return v.strip()


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="name", message="Name must not be empty")
        return v.strip()


class UserShort(BaseModel):
    id: UUID
    username: str

    class Config:
        from_attributes = True


class RoleRead(RoleBase):
    id: UUID
    users: List[UserShort] = []

    class Config:
        from_attributes = True