from fastapi import APIRouter, Depends, Response
from uuid import UUID
from typing import List
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate
from src.services.application import ApplicationService

router = APIRouter(prefix="/api/v1/applications", tags=["Applications"])


def get_application_service(session: AsyncSession = Depends(get_session)) -> ApplicationService:
    return ApplicationService(session)


@router.post("/", response_model=ApplicationRead, status_code=HTTPStatus.CREATED)
async def create_application(
    data: ApplicationCreate,
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationRead:
    return await service.create(data)


@router.get("/", response_model=List[ApplicationRead], status_code=HTTPStatus.OK)
async def get_applications(
    skip: int = 0,
    limit: int = 100,
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
) -> Response:
    await service.delete(app_id)
    return Response(status_code=HTTPStatus.NO_CONTENT)