from __future__ import annotations
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from src.models.base import Base

if TYPE_CHECKING:
    from src.schemas.comment import CommentBase


class CommentModel(Base):
    __tablename__ = 'comments'

    text: Mapped[str] = mapped_column(sa.Text, nullable=False)

    application_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('applications.id', ondelete="CASCADE"),
        nullable=False
    )

    application: Mapped["ApplicationModel"] = relationship(
        "ApplicationModel", back_populates="comments"
    )

    @classmethod
    def from_schema(cls, data: CommentBase, application_id: UUID) -> CommentModel:
        return cls(**data.model_dump(), application_id=application_id)
