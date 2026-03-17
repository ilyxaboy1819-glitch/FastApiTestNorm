import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from src.models.base import Base, TimestampMixin
from src.models.user import user_roles


class RoleModel(Base, TimestampMixin):
    __tablename__ = 'roles'

    name: Mapped[str] = mapped_column(sa.String(), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)

    users: Mapped[List["UserModel"]] = relationship(
        "UserModel", secondary=user_roles, back_populates="roles"
    )
