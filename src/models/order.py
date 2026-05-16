import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from enum import Enum
from typing import Optional

from src.models.base import Base


class OrderStatus(str, Enum):
    NEW = "new"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


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
