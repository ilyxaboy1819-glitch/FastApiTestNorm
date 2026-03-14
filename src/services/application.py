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
from src.schemas.category import CategoryCreate, CategoryUpdate
from src.schemas.comment import CommentCreate, CommentUpdate
from src.exceptions import NotFoundException, AlreadyExistsException

logger = logging.getLogger(__name__)


class ApplicationService:

    def __init__(self, session: AsyncSession):
        self.session = session

    def _app_options(self):
        return [
            selectinload(ApplicationModel.user),
            selectinload(ApplicationModel.categories),
            selectinload(ApplicationModel.comments),
        ]

    async def _get_app_with_relations(self, app_id: UUID) -> ApplicationModel:
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(*self._app_options())
            .where(ApplicationModel.id == app_id)
        )
        return result.scalar_one()


    async def create(self, data: ApplicationCreate) -> ApplicationModel:
        app = ApplicationModel(**data.model_dump(exclude={"categories"}))
        self.session.add(app)
        await self.session.flush()

        await self.session.refresh(app, ["categories"])

        for cat in data.categories:
            result = await self.session.execute(
                sa.select(CategoryModel).where(CategoryModel.name == cat.name)
            )
            category = result.scalar_one_or_none()
            if not category:
                category = CategoryModel(name=cat.name)
                self.session.add(category)
                await self.session.flush()
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

    async def update(self, app_id: UUID, data: ApplicationUpdate) -> ApplicationModel:
        app = await self.session.get(ApplicationModel, app_id)
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")

        for field, value in data.model_dump(exclude_unset=True, exclude={"categories"}).items():
            setattr(app, field, value)

        if data.categories is not None:
            await self.session.refresh(app, ["categories"])
            app.categories.clear()
            for cat in data.categories:
                result = await self.session.execute(
                    sa.select(CategoryModel).where(CategoryModel.name == cat.name)
                )
                category = result.scalar_one_or_none()
                if not category:
                    category = CategoryModel(name=cat.name)
                    self.session.add(category)
                    await self.session.flush()
                app.categories.append(category)

        await self.session.flush()
        logger.info(f"Application updated with id={app_id}")
        return await self._get_app_with_relations(app_id)

    async def delete(self, app_id: UUID) -> None:
        app = await self.session.get(ApplicationModel, app_id)
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")
        await self.session.delete(app)
        logger.info(f"Application deleted with id={app_id}")


    async def create_category(self, data: CategoryCreate) -> CategoryModel:
        existing = await self.session.execute(
            sa.select(CategoryModel).where(CategoryModel.name == data.name)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Category with name '{data.name}' already exists")
            raise AlreadyExistsException("Category with this name already exists")

        category = CategoryModel(**data.model_dump())
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        logger.info(f"Category created with id={category.id}")
        return category

    async def get_all_categories(self, skip: int = 0, limit: int = 100) -> List[CategoryModel]:
        logger.info(f"Getting categories skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(CategoryModel).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_category_by_id(self, cat_id: UUID) -> CategoryModel:
        category = await self.session.get(CategoryModel, cat_id)
        if not category:
            logger.warning(f"Category with id={cat_id} not found")
            raise NotFoundException(f"Category with id={cat_id} not found")
        return category

    async def update_category(self, cat_id: UUID, data: CategoryUpdate) -> CategoryModel:
        category = await self.session.get(CategoryModel, cat_id)
        if not category:
            logger.warning(f"Category with id={cat_id} not found")
            raise NotFoundException(f"Category with id={cat_id} not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        await self.session.flush()
        await self.session.refresh(category)
        logger.info(f"Category updated with id={cat_id}")
        return category

    async def delete_category(self, cat_id: UUID) -> None:
        category = await self.session.get(CategoryModel, cat_id)
        if not category:
            logger.warning(f"Category with id={cat_id} not found")
            raise NotFoundException(f"Category with id={cat_id} not found")
        await self.session.delete(category)
        logger.info(f"Category deleted with id={cat_id}")


    async def _get_comment_with_relations(self, comment_id: UUID) -> CommentModel:
        result = await self.session.execute(
            sa.select(CommentModel)
            .options(selectinload(CommentModel.application))
            .where(CommentModel.id == comment_id)
        )
        return result.scalar_one()

    async def create_comment(self, app_id: UUID, data: CommentCreate) -> CommentModel:
        application = await self.session.get(ApplicationModel, app_id)
        if not application:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")

        comment = CommentModel(**data.model_dump(), application_id=app_id)
        self.session.add(comment)
        await self.session.flush()
        logger.info(f"Comment created with id={comment.id} for application_id={app_id}")
        return await self._get_comment_with_relations(comment.id)

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
        comment = await self.session.get(CommentModel, comment_id)
        if not comment:
            logger.warning(f"Comment with id={comment_id} not found")
            raise NotFoundException(f"Comment with id={comment_id} not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(comment, field, value)

        await self.session.flush()
        logger.info(f"Comment updated with id={comment_id}")
        return await self._get_comment_with_relations(comment_id)

    async def delete_comment(self, comment_id: UUID) -> None:
        comment = await self.session.get(CommentModel, comment_id)
        if not comment:
            logger.warning(f"Comment with id={comment_id} not found")
            raise NotFoundException(f"Comment with id={comment_id} not found")
        await self.session.delete(comment)
        logger.info(f"Comment deleted with id={comment_id}")