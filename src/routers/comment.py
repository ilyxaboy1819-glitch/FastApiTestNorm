from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import List
from http import HTTPStatus

from src.dependencies import get_application_service
from src.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from src.services.application import ApplicationService

router = APIRouter(prefix="/api/v1/comments", tags=["Comments"])


@router.post("/applications/{app_id}", response_model=CommentRead, status_code=HTTPStatus.CREATED)
async def create_comment(
    app_id: UUID,
    data: CommentCreate,
    service: ApplicationService = Depends(get_application_service),
) -> CommentRead:
    return await service.create_comment(app_id, data)


@router.get("/", response_model=List[CommentRead], status_code=HTTPStatus.OK)
async def get_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: ApplicationService = Depends(get_application_service),
) -> List[CommentRead]:
    return await service.get_all_comments(skip=skip, limit=limit)


@router.get("/{comment_id}", response_model=CommentRead, status_code=HTTPStatus.OK)
async def get_comment(
    comment_id: UUID,
    service: ApplicationService = Depends(get_application_service),
) -> CommentRead:
    return await service.get_comment_by_id(comment_id)


@router.put("/{comment_id}", response_model=CommentRead, status_code=HTTPStatus.OK)
async def update_comment(
    comment_id: UUID,
    data: CommentUpdate,
    service: ApplicationService = Depends(get_application_service),
) -> CommentRead:
    return await service.update_comment(comment_id, data)


@router.delete("/{comment_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    service: ApplicationService = Depends(get_application_service),
) -> None:
    await service.delete_comment(comment_id)