import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from uuid import UUID
from typing import Optional

from src.models.base import Base


class OutboxModel(Base):
    __tablename__ = "outbox"

    aggregate_type: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    aggregate_id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    topic: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    payload_json: Mapped[str] = mapped_column(sa.Text, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(sa.String(255), nullable=False, unique=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
