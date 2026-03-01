from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class ProfileBase(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


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