import uuid
from unittest.mock import AsyncMock, patch

import pytest

from src.exceptions import NotFoundException
from src.schemas.order import OrderCreate, OrderItemCreate
from src.schemas.user import UserRead
from src.schemas.application import ApplicationRead
from src.services.application import ApplicationService


def _make_user_read(**kwargs) -> UserRead:
    defaults = dict(
        id=uuid.uuid4(),
        username="testuser",
        email="test@example.com",
        full_name=None,
        profile=None,
        roles=[],
    )
    defaults.update(kwargs)
    return UserRead(**defaults)


@pytest.fixture
def mock_order_client():
    return AsyncMock()


@pytest.fixture
def mock_user_service():
    service = AsyncMock()
    service.get_by_id.return_value = _make_user_read()
    return service


@pytest.fixture
def mock_app_repo():
    return AsyncMock()


@pytest.fixture
def mock_order_repo():
    return AsyncMock()


@pytest.fixture
def application_service(mock_order_client, mock_user_service, mock_app_repo, mock_order_repo):
    return ApplicationService(
        repository=mock_app_repo,
        order_repo=mock_order_repo,
        order_client=mock_order_client,
        user_service=mock_user_service,
    )


def _make_order_create() -> OrderCreate:
    return OrderCreate(
        user_id=uuid.uuid4(),
        items=[OrderItemCreate(
            application_id=uuid.uuid4(),
            quantity=2,
            price=10.0,
        )],
    )


class TestOrderServiceValidation:

    @pytest.mark.asyncio
    @patch("src.services.application.get_cached", return_value=None)
    async def test_user_not_found_does_not_start_saga(
        self, mock_cache, application_service, mock_user_service, mock_order_repo, mock_order_client
    ):
        mock_user_service.get_by_id.side_effect = NotFoundException("User not found")

        with pytest.raises(NotFoundException):
            await application_service.create_order(_make_order_create())

        mock_order_repo.create.assert_not_called()
        mock_order_client.create_order.assert_not_called()
