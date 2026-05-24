import json
import logging
from uuid import UUID

from src.clients.order_service import OrderServiceClient
from src.services.user import UserService
from src.services.application import ApplicationService
from src.repositories.order import OrderRepository
from src.models.order import LocalOrderModel, OrderStatus
from src.schemas.order import (
    OrderCreate, OrderEnriched, OrderResponse,
    OrderItemPayload, OrderPayload,
)
from src.exceptions import NotFoundException
from src.cache import get_cached, set_cached

logger = logging.getLogger(__name__)

CACHE_PREFIX = "order"


class OrderService:

    def __init__(
        self,
        order_client: OrderServiceClient,
        user_service: UserService,
        app_service: ApplicationService,
        order_repo: OrderRepository,
    ):
        self.order_client = order_client
        self.user_service = user_service
        self.app_service = app_service
        self.order_repo = order_repo

    async def create(self, data: OrderCreate) -> OrderEnriched:
        user = await self.user_service.get_by_id(data.user_id)

        items_payload = []
        for item in data.items:
            app = await self.app_service.get_by_id(item.application_id)
            items_payload.append(OrderItemPayload(
                application_id=str(item.application_id),
                quantity=item.quantity,
                price=item.price,
                application_name=app.title,
                application_category=None,
            ))

        payload = OrderPayload(
            user_id=str(data.user_id),
            user_email=user.email,
            user_name=user.username,
            items=items_payload,
        )

        local_order = LocalOrderModel(
            user_id=data.user_id,
            status=OrderStatus.NEW.value,
        )
        local_order = await self.order_repo.create(local_order)
        logger.info(f"Local order created with id={local_order.id}, status=NEW")

        try:
            remote_order = await self.order_client.create_order(payload)

            await self.order_repo.update_status(
                local_order.id,
                OrderStatus.CONFIRMED.value,
                external_id=remote_order.id,
            )
            logger.info(f"Local order {local_order.id} confirmed, external_id={remote_order.id}")

            return self._to_enriched(remote_order, local_order.id, OrderStatus.CONFIRMED.value)

        except Exception as e:
            await self.order_repo.update_status(
                local_order.id,
                OrderStatus.CANCELLED.value,
            )
            logger.error(f"Order saga failed for local_order={local_order.id}: {e}")
            raise

    async def get_by_id(self, order_id: UUID) -> OrderEnriched:
        cache_key = f"{CACHE_PREFIX}:{order_id}"
        cached = await get_cached(cache_key)
        if cached:
            return OrderEnriched.model_validate(json.loads(cached))

        local_order = await self.order_repo.get_by_id(order_id)
        if not local_order:
            raise NotFoundException(f"Order with id={order_id} not found")

        if not local_order.external_id:
            return OrderEnriched(
                id=local_order.id,
                user_id=local_order.user_id,
                status=local_order.status,
                items=[],
                created_at=local_order.created_at,
                updated_at=local_order.updated_at,
            )

        remote_order = await self.order_client.get_order(local_order.external_id)

        result = self._to_enriched(remote_order, local_order.id, local_order.status)
        await set_cached(cache_key, json.dumps(result.model_dump(mode="json")))
        return result

    @staticmethod
    def _to_enriched(
        remote: OrderResponse,
        local_id: UUID,
        local_status: str,
    ) -> OrderEnriched:
        return OrderEnriched(
            id=local_id,
            user_id=remote.user_id,
            status=local_status,
            items=remote.items,
            created_at=remote.created_at,
            updated_at=remote.updated_at,
            user_username=remote.user_name,
            user_email=remote.user_email,
        )
