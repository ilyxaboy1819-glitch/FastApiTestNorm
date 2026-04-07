import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from src.models.base import Base


class CategoryModel(Base):
    __tablename__ = 'categories'

    name: Mapped[str] = mapped_column(sa.String(), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)

    applications: Mapped[List["ApplicationModel"]] = relationship(
        "ApplicationModel",
        back_populates="category",
    )
