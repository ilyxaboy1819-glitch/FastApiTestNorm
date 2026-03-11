from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.comment import CommentModel
from src.models.application import ApplicationModel
from src.schemas.comment import CommentCreate, CommentUpdate
from src.exceptions import NotFoundException


class CommentService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_with_relations(self, comment_id: UUID) -> CommentModel:
        result = await self.session.execute(
            sa.select(CommentModel)
            .options(selectinload(CommentModel.application))
            .where(CommentModel.id == comment_id)
        )
        return result.scalar_one()

    async def create(self, app_id: UUID, data: CommentCreate) -> CommentModel:
        application = await self.session.get(ApplicationModel, app_id)
        if not application:
            raise NotFoundException("Application not found")

        comment = CommentModel(**data.model_dump(), application_id=app_id)
        self.session.add(comment)
        await self.session.flush()
        return await self._get_with_relations(comment.id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[CommentModel]:
        result = await self.session.execute(
            sa.select(CommentModel)
            .options(selectinload(CommentModel.application))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, comment_id: UUID) -> CommentModel:
        result = await self.session.execute(
            sa.select(CommentModel)
            .options(selectinload(CommentModel.application))
            .where(CommentModel.id == comment_id)
        )
        comment = result.scalar_one_or_none()
        if not comment:
            raise NotFoundException("Comment not found")
        return comment

    async def update(self, comment_id: UUID, data: CommentUpdate) -> CommentModel:
        comment = await self.session.get(CommentModel, comment_id)
        if not comment:
            raise NotFoundException("Comment not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(comment, field, value)

        await self.session.flush()
        return await self._get_with_relations(comment_id)

    async def delete(self, comment_id: UUID) -> None:
        comment = await self.session.get(CommentModel, comment_id)
        if not comment:
            raise NotFoundException("Comment not found")
        await self.session.delete(comment)