import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from src.models.base import Base
from src.models.application import application_category


class CategoryModel(Base):
    __tablename__ = 'categories'

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(sa.String(), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)

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

    applications: Mapped[List["ApplicationModel"]] = relationship(
        "ApplicationModel", secondary=application_category, back_populates="categories"
    )