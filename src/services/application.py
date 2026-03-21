import logging
from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.application import ApplicationModel
from src.models.category import CategoryModel
from src.models.comment import CommentModel
from src.models.user import UserModel
from src.schemas.application import ApplicationCreate, ApplicationUpdate
from src.schemas.comment import CommentCreate
from src.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class ApplicationService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ApplicationCreate) -> ApplicationModel:
        user = await self.session.get(UserModel, data.user_id)
        if not user:
            raise ValidationException(field="user_id", message=f"User {data.user_id} does not exist")

        category_ids = [cat.id for cat in data.categories]
        result = await self.session.execute(
            sa.select(CategoryModel).where(CategoryModel.id.in_(category_ids))
        )
        categories = list(result.scalars().all())
        if len(categories) != len(category_ids):
            raise ValidationException(field="categories", message="One or more categories not found")

        app = ApplicationModel(**data.model_dump(exclude={"categories"}))
        app.categories = categories
        self.session.add(app)

        logger.info(f"Application created with id={app.id}")
        return app

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ApplicationModel]:
        logger.info(f"Getting applications skip={skip} limit={limit}")
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(
                selectinload(ApplicationModel.categories),
                selectinload(ApplicationModel.comments),
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, app_id: UUID) -> ApplicationModel:
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(
                selectinload(ApplicationModel.categories),
                selectinload(ApplicationModel.comments),
            )
            .where(ApplicationModel.id == app_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")
        return app

    async def update(self, app_id: UUID, data: ApplicationUpdate) -> ApplicationModel:
        app = await self.get_by_id(app_id)

        for field, value in data.model_dump(exclude_unset=True, exclude={"categories"}).items():
            setattr(app, field, value)

        if data.categories is not None:
            category_ids = [cat.id for cat in data.categories]
            result = await self.session.execute(
                sa.select(CategoryModel).where(CategoryModel.id.in_(category_ids))
            )
            categories = list(result.scalars().all())
            if len(categories) != len(category_ids):
                raise ValidationException(field="categories", message="One or more categories not found")

            for category in categories:
                if category not in app.categories:
                    app.categories.append(category)

        logger.info(f"Application updated with id={app_id}")
        return app

    async def delete(self, app_id: UUID) -> None:
        app = await self.session.get(ApplicationModel, app_id)
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")
        await self.session.delete(app)
        logger.info(f"Application deleted with id={app_id}")

    async def create_comment(self, app_id: UUID, data: CommentCreate) -> CommentModel:
        app = await self.session.get(ApplicationModel, app_id)
        if not app:
            raise NotFoundException(f"Application with id={app_id} not found")

        comment = CommentModel(**data.model_dump(), application_id=app_id)
        self.session.add(comment)
        logger.info(f"Comment created for application_id={app_id}")
        return comment
