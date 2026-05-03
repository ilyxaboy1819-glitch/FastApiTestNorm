from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, field_validator

from src.exceptions import ValidationException
from src.models.application import ApplicationModel
from src.models.comment import CommentModel
from src.schemas.comment import CommentBase, CommentShort


class ApplicationBase(BaseModel):
    title: str
    description: Optional[str] = None

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="title", message="Title must not be empty")
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_must_not_be_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValidationException(field="description", message="Description must not be empty if provided")
        return v.strip() if v else v


class ApplicationCreate(ApplicationBase):
    comments: List[CommentBase]

    @field_validator('comments')
    @classmethod
    def comments_must_not_be_empty(cls, v: List[CommentBase]) -> List[CommentBase]:
        if not v:
            raise ValidationException(field="comments", message="Comments must not be empty")
        return v

    def to_model(self, user_id: UUID, category_id: UUID) -> ApplicationModel:
        app = ApplicationModel(**self.model_dump(exclude={"comments"}), user_id=user_id, category_id=category_id)
        app.comments = [CommentModel(text=c.text) for c in self.comments]
        return app


class ApplicationUpdate(BaseModel):
    title: str
    description: Optional[str] = None

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValidationException(field="title", message="Title must not be empty")
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_must_not_be_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValidationException(field="description", message="Description must not be empty if provided")
        return v.strip() if v else v


class ApplicationShort(BaseModel):
    id: UUID
    title: str

    class Config:
        from_attributes = True


class ApplicationRead(ApplicationBase):
    id: UUID
    comments: List[CommentShort] = []

    class Config:
        from_attributes = True

    @classmethod
    def from_model(cls, model: ApplicationModel) -> "ApplicationRead":
        return cls.model_validate(model)

    @classmethod
    def from_list(cls, models) -> List["ApplicationRead"]:
        return [cls.model_validate(m) for m in models]
