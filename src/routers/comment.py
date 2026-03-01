from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import List
import sqlalchemy as sa
from sqlalchemy.orm import selectinload

from src.db import get_session
from src.models.comment import CommentModel
from src.models.application import ApplicationModel
from src.schemas.comment import CommentCreate, CommentRead, CommentUpdate


router = APIRouter(
    prefix="/comments",tags=["Comments"])

@router.post("/applications/{app_id}", response_model=CommentRead)
async def create_comment(app_id: UUID, comment_data: CommentCreate):
    async with get_session() as session:

        application = await session.get(ApplicationModel, app_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        comment = CommentModel(
            text=comment_data.text,
            application_id=app_id
        )

        session.add(comment)
        await session.commit()
        await session.refresh(comment)

        return comment

@router.get("/{comment_id}", response_model=CommentRead)
async def get_comment(comment_id: UUID):
    async with get_session() as session:

        result = await session.execute(
            sa.select(CommentModel)
            .options(selectinload(CommentModel.application))
            .where(CommentModel.id == comment_id)
        )

        comment = result.scalar_one_or_none()

        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        return comment

@router.get("/", response_model=List[CommentRead])
async def get_comments(skip: int = 0, limit: int = 100):
    async with get_session() as session:

        result = await session.execute(
            sa.select(CommentModel)
            .options(selectinload(CommentModel.application))
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

@router.put("/{comment_id}", response_model=CommentRead)
async def update_comment(comment_id: UUID, comment_data: CommentUpdate):
    async with get_session() as session:

        comment = await session.get(CommentModel, comment_id)

        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        for field, value in comment_data.model_dump(exclude_unset=True).items():
            setattr(comment, field, value)

        await session.commit()
        await session.refresh(comment)

        return comment

@router.delete("/{comment_id}", status_code=204)
async def delete_comment(comment_id: UUID):
    async with get_session() as session:

        comment = await session.get(CommentModel, comment_id)

        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        await session.delete(comment)
        await session.commit()

        return None