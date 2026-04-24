from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.services.application import ApplicationService
from src.services.role import RoleService
from src.services.user import UserService


def get_application_service(session: AsyncSession = Depends(get_session)) -> ApplicationService:
    return ApplicationService(session)


def get_role_service(session: AsyncSession = Depends(get_session)) -> RoleService:
    return RoleService(session)


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)