from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import List
from http import HTTPStatus

from src.dependencies import get_application_service
from src.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate
from src.services.application import ApplicationService

router = APIRouter(prefix="/api/v1/applications", tags=["Applications"])


@router.post("/", response_model=ApplicationRead, status_code=HTTPStatus.CREATED)
async def create_application(
    data: ApplicationCreate,
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationRead:
    return await service.create(data)


@router.get("/", response_model=List[ApplicationRead], status_code=HTTPStatus.OK)
async def get_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: ApplicationService = Depends(get_application_service),
) -> List[ApplicationRead]:
    return await service.get_all(skip=skip, limit=limit)

@router.get("/{app_id}", response_model=ApplicationRead, status_code=HTTPStatus.OK)
async def get_application(
    app_id: UUID,
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationRead:
    return await service.get_by_id(app_id)


@router.put("/{app_id}", response_model=ApplicationRead, status_code=HTTPStatus.OK)
async def update_application(
    app_id: UUID,
    data: ApplicationUpdate,
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationRead:
    return await service.update(app_id, data)


@router.delete("/{app_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_application(
    app_id: UUID,
    service: ApplicationService = Depends(get_application_service),
) -> None:
    await service.delete(app_id)