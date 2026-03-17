import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from src.models.base import Base, TimestampMixin


class CommentModel(Base, TimestampMixin):
    __tablename__ = 'comments'

    text: Mapped[str] = mapped_column(sa.Text, nullable=False)

    application_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('applications.id', ondelete="CASCADE"),
        nullable=False
    )

    application: Mapped["ApplicationModel"] = relationship(
        "ApplicationModel", back_populates="comments"
    )
