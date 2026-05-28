import pytest
from pydantic import ValidationError

from src.schemas.user import UserCreate, UserUpdate
from src.schemas.profile import ProfileBase
from src.exceptions import ValidationException


class TestUserValidation:

    def test_valid_user_create(self):
        user = UserCreate(
            username="valid",
            email="valid@example.com",
            profile=ProfileBase(bio="hello")
        )
        assert user.username == "valid"

    def test_empty_username(self):
        with pytest.raises(ValidationException):
            UserCreate(username="   ", email="test@example.com", profile=ProfileBase(bio="bio"))

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(username="test", email="not-an-email", profile=ProfileBase(bio="bio"))

    def test_whitespace_full_name(self):
        with pytest.raises(ValidationException):
            UserCreate(username="test", email="test@example.com", full_name="   ", profile=ProfileBase(bio="bio"))

    def test_valid_update(self):
        update = UserUpdate(username="updated", email="up@example.com")
        assert update.username == "updated"

    def test_empty_username_update(self):
        with pytest.raises(ValidationException):
            UserUpdate(username="  ", email="up@example.com")
