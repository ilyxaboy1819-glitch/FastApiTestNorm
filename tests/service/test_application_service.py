import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from src.models.application import ApplicationModel
from src.schemas.application import ApplicationCreate, ApplicationUpdate
from src.schemas.comment import CommentBase
from src.services.application import ApplicationService
from src.exceptions import NotFoundException


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return ApplicationService(mock_repo)


def _make_app(app_id=None):
    app = MagicMock(spec=ApplicationModel)
    app.id = app_id or uuid4()
    app.title = "Test App"
    app.description = "desc"
    app.comments = []
    app.is_deleted = False
    return app


class TestApplicationService:

    @patch("src.services.application.delete_cached_pattern", new_callable=AsyncMock)
    async def test_create_success(self, mock_cache, service, mock_repo):
        app = _make_app()
        mock_repo.create.return_value = app

        data = ApplicationCreate(title="Test App", description="desc", comments=[CommentBase(text="c1")])
        result = await service.create(data, uuid4(), uuid4())

        assert result.title == "Test App"
        mock_repo.create.assert_called_once()

    @patch("src.services.application.get_cached", new_callable=AsyncMock, return_value=None)
    @patch("src.services.application.set_cached", new_callable=AsyncMock)
    async def test_get_by_id_success(self, mock_set, mock_get, service, mock_repo):
        app = _make_app()
        mock_repo.get_by_id.return_value = app

        result = await service.get_by_id(app.id)
        assert result.title == "Test App"

    @patch("src.services.application.get_cached", new_callable=AsyncMock, return_value=None)
    async def test_get_by_id_not_found(self, mock_get, service, mock_repo):
        mock_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.get_by_id(uuid4())

    @patch("src.services.application.delete_cached", new_callable=AsyncMock)
    @patch("src.services.application.delete_cached_pattern", new_callable=AsyncMock)
    async def test_delete_success(self, mock_pattern, mock_del, service, mock_repo):
        app = _make_app()
        mock_repo.get_by_id.return_value = app

        await service.delete(app.id)
        mock_repo.soft_delete.assert_called_once_with(app.id)

    async def test_delete_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.delete(uuid4())
