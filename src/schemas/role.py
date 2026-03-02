from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


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
