from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class UserShort(BaseModel):
    id: UUID
    username: str

    class Config:
        from_attributes = True


class RoleRead(RoleBase):
    id: UUID
    users: List[UserShort] = Field(default_factory=list)

    class Config:
        from_attributes = True