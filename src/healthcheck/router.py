from fastapi import APIRouter
from pydantic import BaseModel
from http import HTTPStatus


class HealthcheckResponse(BaseModel):
    status: str


router = APIRouter(tags=["Health"], prefix="/api/v1")


@router.get("/healthcheck", response_model=HealthcheckResponse, status_code=HTTPStatus.OK)
async def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(status="ok")