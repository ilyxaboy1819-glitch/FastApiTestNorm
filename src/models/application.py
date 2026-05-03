import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from typing import List, Optional
from src.models.base import Base


class ApplicationModel(Base):
    __tablename__ = 'applications'

    title: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)

    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False
    )

    category_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('categories.id', ondelete="CASCADE"),
        nullable=False
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="applications",
    )

    category: Mapped["CategoryModel"] = relationship(
        "CategoryModel",
        back_populates="applications",
    )

    comments: Mapped[List["CommentModel"]] = relationship(
        "CommentModel",
        back_populates="application",
        cascade="all, delete-orphan",
    )

