from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from typing import Optional, List


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

    @field_validator('username')
    @classmethod
    def username_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Username must not be empty')
        return v.strip()


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

    @field_validator('username')
    @classmethod
    def username_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Username must not be empty')
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