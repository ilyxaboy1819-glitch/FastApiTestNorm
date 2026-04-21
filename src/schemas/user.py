from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from typing import Optional, List

from src.exceptions import ValidationException
from src.schemas.profile import ProfileBase


class RoleShort(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class ProfileShort(BaseModel):
    id: UUID
    bio: Optional[str] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    profile: ProfileBase

    @field_validator('username')
    @classmethod
    def username_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="username", message="Username must not be empty")
        return v.strip()

    @field_validator('email')
    @classmethod
    def email_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="email", message="Email must not be empty")
        return v.strip()

    @field_validator('full_name')
    @classmethod
    def full_name_must_not_be_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValidationException(field="full_name", message="Full name must not be empty if provided")
        return v.strip() if v else v


class UserUpdate(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    profile: Optional[ProfileBase] = None

    @field_validator('username')
    @classmethod
    def username_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="username", message="Username must not be empty")
        return v.strip()

    @field_validator('email')
    @classmethod
    def email_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="email", message="Email must not be empty")
        return v.strip()

    @field_validator('full_name')
    @classmethod
    def full_name_must_not_be_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValidationException(field="full_name", message="Full name must not be empty if provided")
        return v.strip() if v else v


class UserRead(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    profile: Optional[ProfileShort] = None
    roles: List[RoleShort] = []

    class Config:
        from_attributes = True