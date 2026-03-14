from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class ProfileBase(BaseModel):
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, min_length=5, max_length=20)


class ProfileCreate(ProfileBase):
    user_id: UUID


class ProfileUpdate(ProfileBase):
    pass


class UserShort(BaseModel):
    id: UUID
    username: str

    class Config:
        from_attributes = True


class ProfileRead(ProfileBase):
    id: UUID
    user: UserShort

    class Config:
        from_attributes = True