import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from src.models.base import Base


user_roles = sa.Table(
    'user_roles',
    Base.metadata,
    sa.Column('user_id', sa.ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    sa.Column('role_id', sa.ForeignKey('roles.id', ondelete="CASCADE"), primary_key=True)
)


class UserModel(Base):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(sa.String(), nullable=False)
    email: Mapped[str] = mapped_column(sa.String(), unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)

    applications: Mapped[List["ApplicationModel"]] = relationship(
        "ApplicationModel", back_populates="user", cascade="all, delete-orphan"
    )
    profile: Mapped[Optional["ProfileModel"]] = relationship(
        "ProfileModel", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    roles: Mapped[List["RoleModel"]] = relationship(
        "RoleModel", secondary=user_roles, back_populates="users"
    )

