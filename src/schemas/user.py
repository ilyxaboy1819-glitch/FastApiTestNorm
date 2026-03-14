from pydantic import BaseModel, EmailStr, Field
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
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)


class UserRead(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    profile: Optional[ProfileShort] = None
    roles: List[RoleShort] = []

    class Config:
        from_attributes = True