import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from typing import Optional
from src.models.base import Base


class ProfileModel(Base):
    __tablename__ = 'profiles'

    bio: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(sa.String(), nullable=True)

    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('users.id', ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="profile",
    )
