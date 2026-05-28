import logging
from http import HTTPStatus
from uuid import UUID

import httpx
import pybreaker

from src.config import Settings
from src.exceptions import NotFoundException, OrderServiceError
from src.schemas.order import OrderPayload, OrderResponse

settings = Settings()

logger = logging.getLogger(__name__)

order_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=settings.cb_fail_max,
    reset_timeout=settings.cb_reset_timeout,
    name="order-service",
)

_RETRYABLE_STATUSES = {
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
    HTTPStatus.REQUEST_TIMEOUT,
    HTTPStatus.TOO_MANY_REQUESTS,
}


class OrderServiceClient:

    def __init__(self, base_url: str = settings.service2_url) -> None:
        self._base_url = base_url

    async def create_order(self, payload: OrderPayload) -> OrderResponse:
        response = await self._request("POST", "/api/v1/orders/", json=payload.model_dump())

        if response.status_code == HTTPStatus.CREATED:
            return OrderResponse.model_validate(response.json())

        logger.error(f"Order service returned {response.status_code}: {response.text}")
        raise OrderServiceError(f"Order service returned {response.status_code}")

    async def get_order(self, order_id: UUID) -> OrderResponse:
        response = await self._request("GET", f"/api/v1/orders/{order_id}")

        if response.status_code == HTTPStatus.OK:
            return OrderResponse.model_validate(response.json())
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundException(f"Order with id={order_id} not found in order service")

        logger.error(f"Order service returned {response.status_code}: {response.text}")
        raise OrderServiceError(f"Order service returned {response.status_code}")

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        for attempt in range(settings.retry_max_attempts):
            try:
                @order_circuit_breaker
                async def _call():
                    async with httpx.AsyncClient(base_url=self._base_url, timeout=5.0) as client:
                        return await client.request(method, path, **kwargs)

                response = await _call()
            except pybreaker.CircuitBreakerError:
                logger.warning("Circuit breaker OPEN — order service unavailable")
                raise OrderServiceError("Order service is unavailable (circuit breaker open)")
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                if attempt == settings.retry_max_attempts - 1:
                    raise OrderServiceError(f"Order service connection failed: {e}")
                logger.warning(f"Order service request failed (attempt {attempt + 1}): {e}")
                continue

            if response.status_code not in _RETRYABLE_STATUSES:
                return response

            if attempt == settings.retry_max_attempts - 1:
                return response

            logger.warning(f"Order service returned {response.status_code}, retrying (attempt {attempt + 1})")

        return response
