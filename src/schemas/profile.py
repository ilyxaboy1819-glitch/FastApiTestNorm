import re
from uuid import UUID
from typing import Optional
from pydantic import AnyHttpUrl, BaseModel, field_validator

from src.exceptions import ValidationException

RF_PHONE_REGEX = re.compile(r'^(\+7|7|8)\d{10}$')


class ProfileBase(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[AnyHttpUrl] = None
    phone: Optional[str] = None

    @field_validator('bio')
    @classmethod
    def bio_must_not_be_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValidationException(field="bio", message="Bio must not be empty if provided")
        return v.strip() if v else v

    @field_validator('phone')
    @classmethod
    def phone_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if not RF_PHONE_REGEX.match(cleaned):
                raise ValidationException(
                    field="phone",
                    message="Phone must be a valid Russian number: +7XXXXXXXXXX, 7XXXXXXXXXX or 8XXXXXXXXXX"
                )
            return cleaned
        return v


class ProfileCreate(ProfileBase):
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