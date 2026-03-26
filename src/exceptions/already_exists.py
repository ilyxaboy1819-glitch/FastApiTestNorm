from fastapi import HTTPException
from http import HTTPStatus


class AlreadyExistsException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=HTTPStatus.CONFLICT, detail=detail)
