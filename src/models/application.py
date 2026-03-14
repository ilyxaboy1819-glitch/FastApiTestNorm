import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from src.models.base import Base


application_category = sa.Table(
    'application_category',
    Base.metadata,
    sa.Column(
        'application_id',
        sa.ForeignKey('applications.id', ondelete="CASCADE"),
        primary_key=True
    ),
    sa.Column(
        'category_id',
        sa.ForeignKey('categories.id', ondelete="CASCADE"),
        primary_key=True
    )
)


class ApplicationModel(Base):
    __tablename__ = 'applications'

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    title: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)

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

    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="applications",
    )

    categories: Mapped[List["CategoryModel"]] = relationship(
        "CategoryModel",
        secondary=application_category,
        back_populates="applications",
    )

    comments: Mapped[List["CommentModel"]] = relationship(
        "CommentModel",
        back_populates="application",
        cascade="all, delete-orphan",
    )