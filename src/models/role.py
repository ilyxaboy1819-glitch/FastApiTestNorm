import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from src.models.base import Base
from src.models.user import user_roles


class RoleModel(Base):
    __tablename__ = 'roles'

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        server_default=sa.func.now(),
        default=sa.func.now(),
        onupdate=sa.func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=False,
        server_default=sa.text("false")
    )

    users: Mapped[List["UserModel"]] = relationship(
        "UserModel", secondary=user_roles, back_populates="roles"
    )