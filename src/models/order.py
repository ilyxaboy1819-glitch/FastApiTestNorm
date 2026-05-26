import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional

from src.models.base import Base


class OrderStatus(str, Enum):
    NEW = "new"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    ERROR = "error"


class LocalOrderModel(Base):
    __tablename__ = "local_orders"

    external_id: Mapped[Optional[UUID]] = mapped_column(
        sa.UUID(as_uuid=True), nullable=True
    )
    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, server_default=OrderStatus.NEW.value
    )
    retry_count: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default="0"
    )
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    claimed_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    last_error: Mapped[Optional[str]] = mapped_column(
        sa.Text, nullable=True
    )
