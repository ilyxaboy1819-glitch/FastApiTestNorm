import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import List, Optional

from src.db.base import Base
from src.models.application import application_category


class CategoryModel(Base):
    __tablename__ = 'categories'

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    name: Mapped[str] = mapped_column(
        sa.String(100),
        unique=True,
        nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(
        sa.String(255),
        nullable=True
    )

    applications: Mapped[List["ApplicationModel"]] = relationship(
        "ApplicationModel",
        secondary=application_category,
        back_populates="categories",
        lazy="selectin"
    )