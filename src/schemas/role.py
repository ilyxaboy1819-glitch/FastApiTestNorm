from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, field_validator


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name must not be empty')
        return v.strip()


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Name must not be empty')
        return v.strip() if v else v


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