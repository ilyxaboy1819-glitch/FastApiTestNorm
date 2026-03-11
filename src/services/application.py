from uuid import UUID
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.application import ApplicationModel
from src.models.category import CategoryModel
from src.schemas.application import ApplicationCreate, ApplicationUpdate
from src.exceptions import NotFoundException


class ApplicationService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ApplicationCreate) -> ApplicationModel:
        app = ApplicationModel(
            **data.model_dump(exclude={"categories"})
        )
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

        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(
                selectinload(ApplicationModel.user),
                selectinload(ApplicationModel.categories),
                selectinload(ApplicationModel.comments),
            )
            .where(ApplicationModel.id == app.id)
        )
        return result.scalar_one()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ApplicationModel]:
        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(
                selectinload(ApplicationModel.user),
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
                selectinload(ApplicationModel.user),
                selectinload(ApplicationModel.categories),
                selectinload(ApplicationModel.comments),
            )
            .where(ApplicationModel.id == app_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            raise NotFoundException("Application not found")
        return app

    async def update(self, app_id: UUID, data: ApplicationUpdate) -> ApplicationModel:
        app = await self.session.get(ApplicationModel, app_id)
        if not app:
            raise NotFoundException("Application not found")

        update_data = data.model_dump(exclude_unset=True, exclude={"categories"})
        for field, value in update_data.items():
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

        result = await self.session.execute(
            sa.select(ApplicationModel)
            .options(
                selectinload(ApplicationModel.user),
                selectinload(ApplicationModel.categories),
                selectinload(ApplicationModel.comments),
            )
            .where(ApplicationModel.id == app_id)
        )
        return result.scalar_one()

    async def delete(self, app_id: UUID) -> None:
        app = await self.session.get(ApplicationModel, app_id)
        if not app:
            raise NotFoundException("Application not found")
        await self.session.delete(app)