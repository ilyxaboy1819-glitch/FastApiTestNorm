from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import List
import sqlalchemy as sa
from sqlalchemy.orm import selectinload
from src.db import get_session
from src.models.user import UserModel
from src.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


# Создание пользователя
@router.post("/", response_model=UserRead)
async def create_user(user_data: UserCreate):
    async with get_session() as session:

        existing = await session.execute(
            sa.select(UserModel).where(
                (UserModel.username == user_data.username) |
                (UserModel.email == user_data.email)
            )
        )

        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Username or email already exists"
            )

        user = UserModel(**user_data.model_dump())
        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user


# Список пользователей (получить)
@router.get("/", response_model=List[UserRead])
async def get_users(skip: int = 0, limit: int = 100):
    async with get_session() as session:

        result = await session.execute(
            sa.select(UserModel)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.roles)
            )
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()


# Получить одного пользователя
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID):
    async with get_session() as session:

        result = await session.execute(
            sa.select(UserModel)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.roles)
            )
            .where(UserModel.id == user_id)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user


# Обновление пользователя
@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: UUID, user_data: UserUpdate):
    async with get_session() as session:

        user = await session.get(UserModel, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        await session.commit()
        await session.refresh(user)

        return user


# Удаление пользователя
@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: UUID):
    async with get_session() as session:

        user = await session.get(UserModel, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await session.delete(user)
        await session.commit()

        return None