import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime
from src.models.base import Base


class CommentModel(Base):
    __tablename__ = 'comments'

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    text: Mapped[str] = mapped_column(sa.Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        server_default=sa.func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime,
        nullable=True,
        onupdate=sa.func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(
        sa.Boolean,
        server_default=sa.text("false")
    )

    application_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('applications.id', ondelete="CASCADE"),
        nullable=False
    )

    application: Mapped["ApplicationModel"] = relationship(
        "ApplicationModel", back_populates="comments"
    )