import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import List
from src.db.base import Base
from src.models.user import user_roles


class RoleModel(Base):
    __tablename__ = 'roles'

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    name: Mapped[str] = mapped_column(
        sa.String(50),
        unique=True,
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=True
    )

    users: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin"
    )