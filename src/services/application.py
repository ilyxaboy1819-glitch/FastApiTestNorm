import logging
from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.application import ApplicationModel
from src.models.category import CategoryModel
from src.models.comment import CommentModel
from src.schemas.application import ApplicationCreate, ApplicationUpdate
from src.schemas.comment import CommentCreate, CommentUpdate
from src.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class ApplicationService:

    def __init__(self, session: AsyncSession):
        self.session = session

    def _app_options(self):
        return [
            selectinload(ApplicationModel.categories),
            selectinload(ApplicationModel.comments),
        ]

    async def _get_app_with_relations(self, app_id: UUID) -> ApplicationModel:
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(*self._app_options())
            .where(ApplicationModel.id == app_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")
        return app

    async def create(self, data: ApplicationCreate) -> ApplicationModel:
        app = ApplicationModel(**data.model_dump(exclude={"categories"}))
        self.session.add(app)

        for cat in data.categories:
            result = await self.session.execute(
                sa.select(CategoryModel).where(CategoryModel.id == cat.id)
            )
            category = result.scalar_one_or_none()
            if category:
                app.categories.append(category)

        await self.session.flush()
        logger.info(f"Application created with id={app.id}")
        return await self._get_app_with_relations(app.id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ApplicationModel]:
        logger.info(f"Getting applications skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(*self._app_options())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, app_id: UUID) -> ApplicationModel:
        return await self._get_app_with_relations(app_id)

    async def update(self, app_id: UUID, data: ApplicationUpdate) -> ApplicationModel:
        app = await self._get_app_with_relations(app_id)

        for field, value in data.model_dump(exclude_unset=True, exclude={"categories"}).items():
            setattr(app, field, value)

        if data.categories is not None:
            for cat in data.categories:
                result = await self.session.execute(
                    sa.select(CategoryModel).where(CategoryModel.id == cat.id)
                )
                category = result.scalar_one_or_none()
                if category and category not in app.categories:
                    app.categories.append(category)

        logger.info(f"Application updated with id={app_id}")
        return app

    async def delete(self, app_id: UUID) -> None:
        app = await self._get_app_with_relations(app_id)
        await self.session.delete(app)
        logger.info(f"Application deleted with id={app_id}")

    async def create_comment(self, app_id: UUID, data: CommentCreate) -> CommentModel:
        app = await self._get_app_with_relations(app_id)

        comment = CommentModel(**data.model_dump(), application_id=app_id)
        self.session.add(comment)
        logger.info(f"Comment created for application_id={app_id}")
        return comment

    async def get_all_comments(self, skip: int = 0, limit: int = 100) -> List[CommentModel]:
        logger.info(f"Getting comments skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(CommentModel)
            .options(selectinload(CommentModel.application))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_comment_by_id(self, comment_id: UUID) -> CommentModel:
        result = await self.session.execute(
            sa.select(CommentModel)
            .options(selectinload(CommentModel.application))
            .where(CommentModel.id == comment_id)
        )
        comment = result.scalar_one_or_none()
        if not comment:
            logger.warning(f"Comment with id={comment_id} not found")
            raise NotFoundException(f"Comment with id={comment_id} not found")
        return comment

    async def update_comment(self, comment_id: UUID, data: CommentUpdate) -> CommentModel:
        comment = await self.get_comment_by_id(comment_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(comment, field, value)

        logger.info(f"Comment updated with id={comment_id}")
        return comment

    async def delete_comment(self, comment_id: UUID) -> None:
        comment = await self.get_comment_by_id(comment_id)
        await self.session.delete(comment)
        logger.info(f"Comment deleted with id={comment_id}")