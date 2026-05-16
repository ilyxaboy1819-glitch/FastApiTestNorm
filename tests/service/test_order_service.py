import uuid
from unittest.mock import AsyncMock

import pytest

from src.exceptions import NotFoundException
from src.schemas.order import OrderCreate, OrderItemCreate
from src.schemas.user import UserRead
from src.schemas.application import ApplicationRead
from src.services.order import OrderService


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
def mock_app_service():
    service = AsyncMock()
    service.get_by_id.return_value = ApplicationRead(
        id=uuid.uuid4(), title="TestApp", description=None, comments=[]
    )
    return service


@pytest.fixture
def mock_order_repo():
    return AsyncMock()


@pytest.fixture
def order_service(mock_order_client, mock_user_service, mock_app_service, mock_order_repo):
    return OrderService(
        order_client=mock_order_client,
        user_service=mock_user_service,
        app_service=mock_app_service,
        order_repo=mock_order_repo,
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
    async def test_user_not_found_does_not_start_saga(
        self, order_service, mock_user_service, mock_order_repo, mock_order_client
    ):
        mock_user_service.get_by_id.side_effect = NotFoundException("User not found")

        with pytest.raises(NotFoundException):
            await order_service.create(_make_order_create())

        mock_order_repo.create.assert_not_called()
        mock_order_client.create_order.assert_not_called()
