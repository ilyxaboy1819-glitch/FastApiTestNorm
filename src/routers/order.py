from fastapi import APIRouter, Depends
from uuid import UUID
from http import HTTPStatus

from src.dependencies import get_application_service
from src.schemas.order import OrderCreate, OrderEnriched
from src.services.application import ApplicationService

router = APIRouter(prefix="/api/v1", tags=["Orders"])


@router.post("/orders/", response_model=OrderEnriched, status_code=HTTPStatus.CREATED)
async def create_order(
    data: OrderCreate,
    service: ApplicationService = Depends(get_application_service),
) -> OrderEnriched:
    return await service.create_order(data)


@router.get("/orders/{order_id}", response_model=OrderEnriched)
async def get_order(
    order_id: UUID,
    service: ApplicationService = Depends(get_application_service),
) -> OrderEnriched:
    return await service.get_order_by_id(order_id)
