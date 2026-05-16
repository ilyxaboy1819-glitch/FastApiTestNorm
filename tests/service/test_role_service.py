import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from src.models.role import RoleModel
from src.schemas.role import RoleCreate
from src.services.role import RoleService
from src.exceptions import NotFoundException, AlreadyExistsException


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return RoleService(mock_repo)


def _make_role(role_id=None, name="admin"):
    role = MagicMock(spec=RoleModel)
    role.id = role_id or uuid4()
    role.name = name
    role.description = "desc"
    role.users = []
    return role


class TestRoleService:

    @patch("src.services.role.delete_cached_pattern", new_callable=AsyncMock)
    async def test_create_success(self, mock_cache, service, mock_repo):
        mock_repo.get_by_name.return_value = None
        role = _make_role()
        mock_repo.create.return_value = role

        data = RoleCreate(name="admin", description="desc")
        result = await service.create(data)

        assert result.name == "admin"
        mock_repo.create.assert_called_once()

    async def test_create_duplicate(self, service, mock_repo):
        mock_repo.get_by_name.return_value = _make_role()

        data = RoleCreate(name="admin")
        with pytest.raises(AlreadyExistsException):
            await service.create(data)

    @patch("src.services.role.get_cached", new_callable=AsyncMock, return_value=None)
    @patch("src.services.role.set_cached", new_callable=AsyncMock)
    async def test_get_by_id_success(self, mock_set, mock_get, service, mock_repo):
        role = _make_role()
        mock_repo.get_by_id.return_value = role

        result = await service.get_by_id(role.id)
        assert result.name == "admin"

    @patch("src.services.role.get_cached", new_callable=AsyncMock, return_value=None)
    async def test_get_by_id_not_found(self, mock_get, service, mock_repo):
        mock_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.get_by_id(uuid4())

    @patch("src.services.role.delete_cached", new_callable=AsyncMock)
    @patch("src.services.role.delete_cached_pattern", new_callable=AsyncMock)
    async def test_delete_success(self, mock_pattern, mock_del, service, mock_repo):
        role = _make_role()
        mock_repo.get_by_id.return_value = role

        await service.delete(role.id)
        mock_repo.delete.assert_called_once_with(role)
