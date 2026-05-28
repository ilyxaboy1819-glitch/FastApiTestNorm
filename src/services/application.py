import json
import logging
import uuid
from uuid import UUID
from typing import List

import httpx

from src.repositories.application import ApplicationRepository
from src.repositories.order import OrderRepository
from src.clients.order_service import OrderServiceClient
from src.services.user import UserService
from src.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationRead
from src.schemas.order import (
    OrderCreate, OrderEnriched, OrderResponse,
    OrderItemPayload, OrderPayload,
)
from src.models.order import LocalOrderModel, OrderStatus
from src.exceptions import NotFoundException, OrderServiceError
from src.cache import get_cached, set_cached, delete_cached, delete_cached_pattern

logger = logging.getLogger(__name__)

_NETWORK_ERRORS = (
    OrderServiceError,
    httpx.ConnectError,
    httpx.TimeoutException,
)

CACHE_PREFIX = "application"
ORDER_CACHE_PREFIX = "order"


class ApplicationService:

    def __init__(
        self,
        repository: ApplicationRepository,
        order_repository: OrderRepository,
        order_client: OrderServiceClient,
        user_service: UserService,
    ):
        self.repository = repository
        self.order_repository = order_repository
        self.order_client = order_client
        self.user_service = user_service

    async def create(self, data: ApplicationCreate, user_id: UUID, category_id: UUID) -> ApplicationRead:
        app = data.to_model(user_id, category_id)
        app = await self.repository.create(app)
        logger.info(f"Application created with id={app.id}")
        await delete_cached_pattern(f"{CACHE_PREFIX}:list:*")
        return ApplicationRead.from_model(app)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ApplicationRead]:
        cache_key = f"{CACHE_PREFIX}:list:{skip}:{limit}"
        cached = await get_cached(cache_key)
        if cached:
            return [ApplicationRead.model_validate(a) for a in json.loads(cached)]

        logger.info(f"Getting applications skip={skip} limit={limit}")
        apps = await self.repository.get_all(skip, limit)
        result = ApplicationRead.from_list(apps)
        await set_cached(cache_key, json.dumps([a.model_dump(mode="json") for a in result]))
        return result

    async def get_by_id(self, app_id: UUID) -> ApplicationRead:
        cache_key = f"{CACHE_PREFIX}:{app_id}"
        cached = await get_cached(cache_key)
        if cached:
            return ApplicationRead.model_validate(json.loads(cached))

        app = await self.repository.get_by_id(app_id)
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")
        result = ApplicationRead.from_model(app)
        await set_cached(cache_key, json.dumps(result.model_dump(mode="json")))
        return result

    async def update(self, app_id: UUID, data: ApplicationUpdate, category_id: UUID) -> ApplicationRead:
        app = await self.repository.get_by_id(app_id)
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")

        fields = data.model_dump(exclude_unset=True)
        fields["category_id"] = category_id
        await self.repository.update(app_id, fields)
        logger.info(f"Application updated with id={app_id}")
        await delete_cached(f"{CACHE_PREFIX}:{app_id}")
        await delete_cached_pattern(f"{CACHE_PREFIX}:list:*")
        return await self.get_by_id(app_id)

    async def delete(self, app_id: UUID) -> None:
        app = await self.repository.get_by_id(app_id)
        if not app:
            logger.warning(f"Application with id={app_id} not found")
            raise NotFoundException(f"Application with id={app_id} not found")
        await self.repository.soft_delete(app_id)
        logger.info(f"Application soft deleted with id={app_id}")
        await delete_cached(f"{CACHE_PREFIX}:{app_id}")
        await delete_cached_pattern(f"{CACHE_PREFIX}:list:*")

    async def create_order(self, data: OrderCreate) -> OrderEnriched:
        user = await self.user_service.get_by_id(data.user_id)

        app_ids = [item.application_id for item in data.items]
        apps = await self.repository.get_by_ids(app_ids)
        apps_map = {app.id: app for app in apps}

        for app_id in app_ids:
            if app_id not in apps_map:
                raise NotFoundException(f"Application with id={app_id} not found")

        items_payload = []
        for item in data.items:
            app = apps_map[item.application_id]
            items_payload.append(OrderItemPayload(
                application_id=str(item.application_id),
                quantity=item.quantity,
                price=item.price,
                application_name=app.title,
                application_category=None,
            ))

        idempotency_key = str(uuid.uuid4())

        payload = OrderPayload(
            user_id=str(data.user_id),
            user_email=user.email,
            user_name=user.username,
            items=items_payload,
            idempotency_key=idempotency_key,
        )

        local_order = LocalOrderModel(
            user_id=data.user_id,
            status=OrderStatus.PENDING.value,
            idempotency_key=idempotency_key,
            payload_json=payload.model_dump_json(),
        )
        local_order = await self.order_repository.create(local_order)
        logger.info(f"Local order created with id={local_order.id}, status=PENDING")

        try:
            remote_order = await self.order_client.create_order(payload)

            await self.order_repository.update_status(
                local_order.id,
                OrderStatus.CONFIRMED.value,
                expected_status=OrderStatus.PENDING.value,
                external_id=remote_order.id,
            )
            logger.info(f"Local order {local_order.id} confirmed, external_id={remote_order.id}")

            return self._to_enriched(remote_order, local_order.id, OrderStatus.CONFIRMED.value)

        except _NETWORK_ERRORS as e:
            logger.warning(f"Order saga network error for local_order={local_order.id}: {e}")
            return OrderEnriched(
                id=local_order.id,
                user_id=local_order.user_id,
                status=OrderStatus.PENDING.value,
                items=[],
                created_at=local_order.created_at,
                updated_at=local_order.updated_at,
            )

        except Exception as e:
            await self.order_repository.update_status(
                local_order.id,
                OrderStatus.ERROR.value,
                expected_status=OrderStatus.PENDING.value,
            )
            raise

    async def get_order_by_id(self, order_id: UUID) -> OrderEnriched:
        cache_key = f"{ORDER_CACHE_PREFIX}:{order_id}"
        cached = await get_cached(cache_key)
        if cached:
            return OrderEnriched.model_validate(json.loads(cached))

        local_order = await self._get_order_orm(order_id)

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

    async def _get_order_orm(self, order_id: UUID) -> LocalOrderModel:
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise NotFoundException(f"Order with id={order_id} not found")
        return order

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
