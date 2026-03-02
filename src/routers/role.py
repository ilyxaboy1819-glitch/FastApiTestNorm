from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import List
import sqlalchemy as sa
from sqlalchemy.orm import selectinload
from src.db import get_session
from src.models.role import RoleModel
from src.schemas.role import RoleCreate, RoleRead, RoleUpdate


router = APIRouter(
    prefix="/roles",tags=["Roles"])


@router.post("/", response_model=RoleRead)
async def create_role(role_data: RoleCreate):
    async with get_session() as session:

        existing = await session.execute(
            sa.select(RoleModel).where(RoleModel.name == role_data.name)
        )

        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Role with this name already exists"
            )

        role = RoleModel(**role_data.model_dump())
        session.add(role)

        await session.commit()
        await session.refresh(role)

        return role


@router.get("/", response_model=List[RoleRead])
async def get_roles(skip: int = 0, limit: int = 100):
    async with get_session() as session:

        result = await session.execute(
            sa.select(RoleModel)
            .options(selectinload(RoleModel.users))
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()


@router.get("/{role_id}", response_model=RoleRead)
async def get_role(role_id: UUID):
    async with get_session() as session:

        result = await session.execute(
            sa.select(RoleModel)
            .options(selectinload(RoleModel.users))
            .where(RoleModel.id == role_id)
        )

        role = result.scalar_one_or_none()

        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        return role


@router.put("/{role_id}", response_model=RoleRead)
async def update_role(role_id: UUID, role_data: RoleUpdate):
    async with get_session() as session:

        role = await session.get(RoleModel, role_id)

        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        # Проверка уникальности имени
        if role_data.name and role_data.name != role.name:
            existing = await session.execute(
                sa.select(RoleModel).where(RoleModel.name == role_data.name)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail="Role with this name already exists"
                )

        for field, value in role_data.model_dump(exclude_unset=True).items():
            setattr(role, field, value)

        await session.commit()
        await session.refresh(role)

        return role


@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: UUID):
    async with get_session() as session:

        role = await session.get(RoleModel, role_id)

        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        await session.delete(role)
        await session.commit()

        return None