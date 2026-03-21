from fastapi import APIRouter
from http import HTTPStatus

from src.schemas.healthcheck import HealthcheckResponse

router = APIRouter(tags=["Health"], prefix="/api/v1")


@router.get("/healthcheck", response_model=HealthcheckResponse, status_code=HTTPStatus.OK)
async def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(status="ok")
