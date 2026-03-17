from uuid import UUID
from typing import Optional
from pydantic import BaseModel, field_validator


class ProfileBase(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def phone_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 5:
            raise ValueError('Phone must be at least 5 characters')
        return v.strip() if v else v


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