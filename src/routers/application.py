from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import List
from http import HTTPStatus

from src.dependencies import get_application_service
from src.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate
from src.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from src.services.application import ApplicationService

router = APIRouter(prefix="/api/v1", tags=["Applications"])


@router.post("/applications/", response_model=ApplicationRead, status_code=HTTPStatus.CREATED)
async def create_application(
    data: ApplicationCreate,
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationRead:
    return await service.create(data)


@router.get("/applications/", response_model=List[ApplicationRead], status_code=HTTPStatus.OK)
async def get_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: ApplicationService = Depends(get_application_service),
) -> List[ApplicationRead]:
    return await service.get_all(skip=skip, limit=limit)


@router.get("/applications/{app_id}", response_model=ApplicationRead, status_code=HTTPStatus.OK)
async def get_application(
    app_id: UUID,
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationRead:
    return await service.get_by_id(app_id)


@router.put("/applications/{app_id}", response_model=ApplicationRead, status_code=HTTPStatus.OK)
async def update_application(
    app_id: UUID,
    data: ApplicationUpdate,
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationRead:
    return await service.update(app_id, data)


@router.delete("/applications/{app_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_application(
    app_id: UUID,
    service: ApplicationService = Depends(get_application_service),
) -> None:
    await service.delete(app_id)


@router.post("/applications/{app_id}/comments/", response_model=CommentRead, status_code=HTTPStatus.CREATED)
async def create_comment(
    app_id: UUID,
    data: CommentCreate,
    service: ApplicationService = Depends(get_application_service),
) -> CommentRead:
    return await service.create_comment(app_id, data)


@router.get("/comments/", response_model=List[CommentRead], status_code=HTTPStatus.OK)
async def get_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: ApplicationService = Depends(get_application_service),
) -> List[CommentRead]:
    return await service.get_all_comments(skip=skip, limit=limit)


@router.get("/comments/{comment_id}", response_model=CommentRead, status_code=HTTPStatus.OK)
async def get_comment(
    comment_id: UUID,
    service: ApplicationService = Depends(get_application_service),
) -> CommentRead:
    return await service.get_comment_by_id(comment_id)


@router.put("/comments/{comment_id}", response_model=CommentRead, status_code=HTTPStatus.OK)
async def update_comment(
    comment_id: UUID,
    data: CommentUpdate,
    service: ApplicationService = Depends(get_application_service),
) -> CommentRead:
    return await service.update_comment(comment_id, data)


@router.delete("/comments/{comment_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    service: ApplicationService = Depends(get_application_service),
) -> None:
    await service.delete_comment(comment_id)