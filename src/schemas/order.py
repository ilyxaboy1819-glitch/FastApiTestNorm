from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    application_id: UUID
    quantity: int = Field(ge=1, le=100)
    price: float = Field(ge=0.0)


class OrderItemPayload(BaseModel):
    application_id: str
    quantity: int
    price: float
    application_name: str | None = None
    application_category: str | None = None


class OrderPayload(BaseModel):
    user_id: str
    user_email: str
    user_name: str
    items: list[OrderItemPayload]
    idempotency_key: str | None = None


class OrderCreate(BaseModel):
    user_id: UUID
    items: list[OrderItemCreate] = Field(min_length=1, max_length=50)


class OrderItemResponse(BaseModel):
    application_id: UUID
    quantity: int
    price: float
    application_name: str | None = None
    application_category: str | None = None


class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    items: list[OrderItemResponse]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None = None
    user_email: str | None = None
    user_name: str | None = None


class OrderEnriched(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime | None = None
    user_username: str | None = None
    user_email: str | None = None
