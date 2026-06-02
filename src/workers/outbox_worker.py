import asyncio
import logging

from aiokafka import AIOKafkaProducer

from src.config import get_settings
from src.db import SessionFactory
from src.repositories.outbox import OutboxRepository

logger = logging.getLogger(__name__)

settings = get_settings()

POLL_INTERVAL = 5
BATCH_SIZE = 100


async def outbox_worker() -> None:
    logger.info("Outbox worker started")
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        enable_idempotence=True,
        acks="all",
    )
    await producer.start()
    try:
        while True:
            try:
                await _process_batch(producer)
            except Exception as e:
                logger.error(f"Outbox worker error: {e}")
            await asyncio.sleep(POLL_INTERVAL)
    finally:
        await producer.stop()


async def _process_batch(producer: AIOKafkaProducer) -> None:
    async with SessionFactory() as session:
        repo = OutboxRepository(session)
        records = await repo.get_unpublished(BATCH_SIZE)
        if not records:
            return

    published_ids = []
    for record in records:
        try:
            await producer.send_and_wait(
                record.topic,
                value=record.payload_json.encode(),
                key=record.idempotency_key.encode(),
            )
            published_ids.append(record.id)
            logger.info(f"Sent outbox record {record.id} to {record.topic}")
        except Exception as e:
            logger.error(f"Failed to send outbox record {record.id}: {e}")

    if published_ids:
        async with SessionFactory() as session:
            repo = OutboxRepository(session)
            await repo.mark_published_batch(published_ids)
            await session.commit()
            logger.info(f"Marked {len(published_ids)} outbox records as published")
