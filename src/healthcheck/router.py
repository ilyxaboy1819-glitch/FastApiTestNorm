from http import HTTPStatus

from fastapi import APIRouter

from src.schemas.healthcheck import HealthcheckResponse

router = APIRouter(tags=["Health"], prefix="/api/v1")


@router.get("/healthcheck", response_model=HealthcheckResponse)
async def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(status=HTTPStatus.OK)
