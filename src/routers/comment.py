from fastapi import APIRouter, Depends, Response
from uuid import UUID
from typing import List
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from src.services.comment import CommentService

router = APIRouter(prefix="/api/v1/comments", tags=["Comments"])


def get_comment_service(session: AsyncSession = Depends(get_session)) -> CommentService:
    return CommentService(session)


@router.post("/applications/{app_id}", response_model=CommentRead, status_code=HTTPStatus.CREATED)
async def create_comment(
    app_id: UUID,
    data: CommentCreate,
    service: CommentService = Depends(get_comment_service),
) -> CommentRead:
    return await service.create(app_id, data)


@router.get("/", response_model=List[CommentRead], status_code=HTTPStatus.OK)
async def get_comments(
    skip: int = 0,
    limit: int = 100,
    service: CommentService = Depends(get_comment_service),
) -> List[CommentRead]:
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{comment_id}", response_model=CommentRead, status_code=HTTPStatus.OK)
async def get_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
) -> CommentRead:
    return await service.get_by_id(comment_id)


@router.put("/{comment_id}", response_model=CommentRead, status_code=HTTPStatus.OK)
async def update_comment(
    comment_id: UUID,
    data: CommentUpdate,
    service: CommentService = Depends(get_comment_service),
) -> CommentRead:
    return await service.update(comment_id, data)


@router.delete("/{comment_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
) -> Response:
    await service.delete(comment_id)
    return Response(status_code=HTTPStatus.NO_CONTENT)