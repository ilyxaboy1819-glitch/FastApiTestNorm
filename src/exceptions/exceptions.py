from fastapi import HTTPException
from http import HTTPStatus


class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=HTTPStatus.NOT_FOUND, detail=detail)


class AlreadyExistsException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=HTTPStatus.CONFLICT, detail=detail)


class ValidationException(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message