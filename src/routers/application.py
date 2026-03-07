from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List
import sqlalchemy as sa
from sqlalchemy.orm import selectinload
from src.db import get_session
from src.models.application import ApplicationModel
from src.models.category import CategoryModel
from src.models.user import UserModel
from src.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
)

async def get_current_user() -> UserModel:
    raise NotImplementedError


router = APIRouter(prefix="/applications",tags=["Applications"],)


@router.post("/", response_model=ApplicationRead)
async def create_application(
    app_data: ApplicationCreate,
    current_user: UserModel = Depends(get_current_user),
):
    async with get_session() as session:

        app = ApplicationModel(
            title=app_data.title,
            description=app_data.description,
            user_id=current_user.id,
        )

        session.add(app)
        await session.flush()

        for cat_name in app_data.categories:
            result = await session.execute(
                sa.select(CategoryModel).where(CategoryModel.name == cat_name)
            )
            category = result.scalar_one_or_none()

            if not category:
                category = CategoryModel(name=cat_name)
                session.add(category)
                await session.flush()

            app.categories.append(category)

        await session.commit()
        await session.refresh(app)

        return app


@router.get("/", response_model=List[ApplicationRead])
async def get_applications(skip: int = 0, limit: int = 100):
    async with get_session() as session:

        result = await session.execute(
            sa.select(ApplicationModel)
            .options(
                selectinload(ApplicationModel.user),
                selectinload(ApplicationModel.categories),
                selectinload(ApplicationModel.comments),
            )
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()


@router.get("/{app_id}", response_model=ApplicationRead)
async def get_application(app_id: UUID):
    async with get_session() as session:

        result = await session.execute(
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
            raise HTTPException(status_code=404, detail="Application not found")

        return app


@router.put("/{app_id}", response_model=ApplicationRead)
async def update_application(app_id: UUID, app_data: ApplicationUpdate):
    async with get_session() as session:

        app = await session.get(ApplicationModel, app_id)

        if not app:
            raise HTTPException(status_code=404, detail="Application not found")

        if app_data.title is not None:
            app.title = app_data.title

        if app_data.description is not None:
            app.description = app_data.description

        if app_data.categories is not None:
            app.categories.clear()

            for cat_name in app_data.categories:
                result = await session.execute(
                    sa.select(CategoryModel).where(CategoryModel.name == cat_name)
                )
                category = result.scalar_one_or_none()

                if not category:
                    category = CategoryModel(name=cat_name)
                    session.add(category)
                    await session.flush()

                app.categories.append(category)

        await session.commit()
        await session.refresh(app)

        return app


@router.delete("/{app_id}", status_code=204)
async def delete_application(app_id: UUID):
    async with get_session() as session:

        app = await session.get(ApplicationModel, app_id)

        if not app:
            raise HTTPException(status_code=404, detail="Application not found")

        await session.delete(app)
        await session.commit()

        return None