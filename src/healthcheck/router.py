from fastapi import APIRouter
from http import HTTPStatus

from src.healthcheck.schemas import HealthcheckResponse

router = APIRouter(tags=["Health"], prefix="/api/v1")


@router.get("/healthcheck", response_model=HealthcheckResponse, status_code=HTTPStatus.OK)
async def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(status=HTTPStatus.OK.phrase)