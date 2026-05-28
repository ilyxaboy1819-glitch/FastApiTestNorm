import pytest
from pydantic import ValidationError

from src.schemas.application import ApplicationCreate, ApplicationUpdate
from src.schemas.comment import CommentBase
from src.exceptions import ValidationException


class TestApplicationValidation:

    def test_valid_create(self):
        app = ApplicationCreate(
            title="Valid",
            description="desc",
            comments=[CommentBase(text="comment")]
        )
        assert app.title == "Valid"

    def test_empty_title(self):
        with pytest.raises(ValidationException):
            ApplicationCreate(title="   ", comments=[CommentBase(text="c")])

    def test_empty_comments(self):
        with pytest.raises(ValidationException):
            ApplicationCreate(title="Valid", comments=[])

    def test_whitespace_description(self):
        with pytest.raises(ValidationException):
            ApplicationCreate(title="Valid", description="   ", comments=[CommentBase(text="c")])

    def test_valid_update(self):
        update = ApplicationUpdate(title="Updated")
        assert update.title == "Updated"

    def test_empty_title_update(self):
        with pytest.raises(ValidationException):
            ApplicationUpdate(title="   ")
