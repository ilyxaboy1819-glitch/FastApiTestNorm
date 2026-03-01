import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import UUID, uuid4
from datetime import datetime


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class BaseServiceModel(Base):
    """Базовый класс для таблиц сервиса с общими полями."""
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def on_conflict_constraint(cls) -> tuple | None:
        return None