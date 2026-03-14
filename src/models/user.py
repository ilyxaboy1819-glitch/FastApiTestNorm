import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from src.models.base import Base


user_roles = sa.Table(
    'user_roles',
    Base.metadata,
    sa.Column('user_id', sa.ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    sa.Column('role_id', sa.ForeignKey('roles.id', ondelete="CASCADE"), primary_key=True)
)


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    email: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)

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

    applications: Mapped[List["ApplicationModel"]] = relationship(
        "ApplicationModel", back_populates="user", cascade="all, delete-orphan"
    )
    profile: Mapped[Optional["ProfileModel"]] = relationship(
        "ProfileModel", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    roles: Mapped[List["RoleModel"]] = relationship(
        "RoleModel", secondary=user_roles, back_populates="users"
    )