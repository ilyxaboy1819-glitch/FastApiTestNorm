import pytest

from src.schemas.role import RoleCreate, RoleUpdate
from src.exceptions import ValidationException


class TestRoleValidation:

    def test_valid_create(self):
        role = RoleCreate(name="admin", description="Admin role")
        assert role.name == "admin"

    def test_empty_name(self):
        with pytest.raises(ValidationException):
            RoleCreate(name="   ")

    def test_whitespace_description(self):
        with pytest.raises(ValidationException):
            RoleCreate(name="admin", description="   ")

    def test_valid_update(self):
        update = RoleUpdate(name="updated")
        assert update.name == "updated"

    def test_empty_name_update(self):
        with pytest.raises(ValidationException):
            RoleUpdate(name="   ")
