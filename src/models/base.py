import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime


class TimestampMixin:
    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
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


class Base(DeclarativeBase):
    pass
