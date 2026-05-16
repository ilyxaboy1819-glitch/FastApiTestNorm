import logging
from http import HTTPStatus
from uuid import UUID

import httpx
import pybreaker
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential, wait_random

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

_RETRYABLE = (OrderServiceError, httpx.ConnectError, httpx.TimeoutException)


def _retry():
    return retry(
        retry=retry_if_exception_type(_RETRYABLE),
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=settings.retry_min_wait,
            max=settings.retry_max_wait,
        ) + wait_random(0, 1),
        reraise=True,
    )


class OrderServiceClient:

    def __init__(self, base_url: str = settings.service2_url) -> None:
        self._base_url = base_url

    @_retry()
    async def create_order(self, payload: OrderPayload) -> OrderResponse:
        try:
            @order_circuit_breaker
            async def _call():
                async with httpx.AsyncClient(base_url=self._base_url, timeout=5.0) as client:
                    return await client.post("/api/v1/orders/", json=payload.model_dump())

            response = await _call()
        except pybreaker.CircuitBreakerError:
            logger.warning("Circuit breaker OPEN — order service unavailable")
            raise OrderServiceError("Order service is unavailable (circuit breaker open)")

        if response.status_code == HTTPStatus.CREATED:
            return OrderResponse.model_validate(response.json())

        logger.error(f"Order service returned {response.status_code}: {response.text}")
        raise OrderServiceError(f"Order service returned {response.status_code}: {response.text}")

    @_retry()
    async def get_order(self, order_id: UUID) -> OrderResponse:
        try:
            @order_circuit_breaker
            async def _call():
                async with httpx.AsyncClient(base_url=self._base_url, timeout=5.0) as client:
                    return await client.get(f"/api/v1/orders/{order_id}")

            response = await _call()
        except pybreaker.CircuitBreakerError:
            logger.warning(f"Circuit breaker OPEN — order service unavailable, order_id={order_id}")
            raise OrderServiceError("Order service is unavailable (circuit breaker open)")

        if response.status_code == HTTPStatus.OK:
            return OrderResponse.model_validate(response.json())
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundException(f"Order with id={order_id} not found in order service")

        logger.error(f"Order service returned {response.status_code}: {response.text}")
        raise OrderServiceError(f"Order service returned {response.status_code}: {response.text}")
