import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from src.exceptions import OrderServiceError
from src.models.order import OrderStatus
from src.schemas.order import (
    OrderCreate, OrderItemCreate, OrderResponse, OrderItemResponse,
)
from src.models.order import LocalOrderModel
from src.schemas.user import UserRead
from src.schemas.application import ApplicationRead, ApplicationModel
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


def _make_remote_order_response(**kwargs) -> OrderResponse:
    defaults = dict(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        status="new",
        items=[OrderItemResponse(
            application_id=uuid.uuid4(),
            quantity=2,
            price=10.0,
            application_name="TestApp",
        )],
        is_deleted=False,
        created_at=datetime.now(timezone.utc),
        user_email="test@example.com",
        user_name="testuser",
    )
    defaults.update(kwargs)
    return OrderResponse(**defaults)


def _make_app_model():
    model = MagicMock()
    model.id = uuid.uuid4()
    model.title = "TestApp"
    model.description = None
    model.comments = []
    model.user_id = uuid.uuid4()
    model.category_id = uuid.uuid4()
    model.is_deleted = False
    model.created_at = datetime.now(timezone.utc)
    model.updated_at = None
    return model


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
    repo = AsyncMock()
    repo.get_by_id.return_value = _make_app_model()
    return repo


@pytest.fixture
def mock_order_repo():
    repo = AsyncMock()
    local = LocalOrderModel(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        status=OrderStatus.NEW.value,
    )
    repo.create.return_value = local
    return repo


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


class TestSagaSuccess:

    @pytest.mark.asyncio
    @patch("src.services.application.set_cached", new_callable=AsyncMock)
    @patch("src.services.application.get_cached", return_value=None)
    async def test_create_saves_local_order_then_confirms(
        self, mock_get_cache, mock_set_cache, application_service, mock_order_repo, mock_order_client
    ):
        remote = _make_remote_order_response()
        mock_order_client.create_order.return_value = remote

        result = await application_service.create_order(_make_order_create())

        mock_order_repo.create.assert_called_once()
        mock_order_client.create_order.assert_called_once()
        mock_order_repo.update_status.assert_called_once_with(
            mock_order_repo.create.return_value.id,
            OrderStatus.CONFIRMED.value,
            external_id=remote.id,
        )
        assert result.status == OrderStatus.CONFIRMED.value
        assert result.user_email == remote.user_email


class TestSagaCompensation:

    @pytest.mark.asyncio
    @patch("src.services.application.set_cached", new_callable=AsyncMock)
    @patch("src.services.application.get_cached", return_value=None)
    async def test_remote_failure_cancels_local_order(
        self, mock_get_cache, mock_set_cache, application_service, mock_order_repo, mock_order_client
    ):
        mock_order_client.create_order.side_effect = OrderServiceError(
            "Order service returned 500"
        )

        with pytest.raises(OrderServiceError):
            await application_service.create_order(_make_order_create())

        mock_order_repo.create.assert_called_once()
        mock_order_repo.update_status.assert_called_once_with(
            mock_order_repo.create.return_value.id,
            OrderStatus.CANCELLED.value,
        )

    @pytest.mark.asyncio
    @patch("src.services.application.set_cached", new_callable=AsyncMock)
    @patch("src.services.application.get_cached", return_value=None)
    async def test_remote_connection_error_cancels_local_order(
        self, mock_get_cache, mock_set_cache, application_service, mock_order_repo, mock_order_client
    ):
        mock_order_client.create_order.side_effect = ConnectionError("connection refused")

        with pytest.raises(ConnectionError):
            await application_service.create_order(_make_order_create())

        mock_order_repo.update_status.assert_called_once_with(
            mock_order_repo.create.return_value.id,
            OrderStatus.CANCELLED.value,
        )

    @pytest.mark.asyncio
    @patch("src.services.application.set_cached", new_callable=AsyncMock)
    @patch("src.services.application.get_cached", return_value=None)
    async def test_local_save_failure_does_not_call_remote(
        self, mock_get_cache, mock_set_cache, application_service, mock_order_repo, mock_order_client
    ):
        mock_order_repo.create.side_effect = Exception("DB connection lost")

        with pytest.raises(Exception, match="DB connection lost"):
            await application_service.create_order(_make_order_create())

        mock_order_client.create_order.assert_not_called()
        mock_order_repo.update_status.assert_not_called()
