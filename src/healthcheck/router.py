from fastapi import APIRouter

from typing import Dict

router = APIRouter(tags=["Health"])


@router.get('/healthcheck')
async def healthcheck() -> Dict[str, str]:
    return {'status': 'ok'}