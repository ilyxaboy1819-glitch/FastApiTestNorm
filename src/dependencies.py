from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.clients.order_service import OrderServiceClient
from src.repositories.user import UserRepository
from src.repositories.application import ApplicationRepository
from src.repositories.role import RoleRepository
from src.repositories.order import OrderRepository
from src.services.application import ApplicationService
from src.services.role import RoleService
from src.services.user import UserService

order_service_client = OrderServiceClient()


def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)


def get_application_repository(session: AsyncSession = Depends(get_session)) -> ApplicationRepository:
    return ApplicationRepository(session)


def get_role_repository(session: AsyncSession = Depends(get_session)) -> RoleRepository:
    return RoleRepository(session)


def get_order_repository(session: AsyncSession = Depends(get_session)) -> OrderRepository:
    return OrderRepository(session)


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)


def get_application_service(
    repo: ApplicationRepository = Depends(get_application_repository),
    order_repo: OrderRepository = Depends(get_order_repository),
    user_service: UserService = Depends(get_user_service),
) -> ApplicationService:
    return ApplicationService(repo, order_repo, order_service_client, user_service)


def get_role_service(repo: RoleRepository = Depends(get_role_repository)) -> RoleService:
    return RoleService(repo)
