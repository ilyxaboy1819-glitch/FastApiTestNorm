from http import HTTPStatus

from pydantic import BaseModel


class HealthcheckResponse(BaseModel):
    status: HTTPStatus
