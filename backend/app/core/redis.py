import json
from typing import AsyncGenerator, Optional
import redis.asyncio as aioredis
from arq.connections import ArqRedis, create_pool, RedisSettings
from app.core.config import settings


_arq_pool: Optional[ArqRedis] = None
_pubsub_pool: Optional[aioredis.Redis] = None


def _get_redis_settings() -> RedisSettings:
    return RedisSettings.from_dsn(settings.REDIS_URL)


async def init_arq_pool() -> None:
    global _arq_pool
    _arq_pool = await create_pool(_get_redis_settings())


async def close_arq_pool() -> None:
    global _arq_pool
    if _arq_pool:
        await _arq_pool.close()
        _arq_pool = None


async def init_pubsub_pool() -> None:
    global _pubsub_pool
    _pubsub_pool = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )


async def close_pubsub_pool() -> None:
    global _pubsub_pool
    if _pubsub_pool:
        await _pubsub_pool.aclose()
        _pubsub_pool = None


def get_arq_pool() -> ArqRedis:
    if _arq_pool is None:
        raise RuntimeError("ARQ pool not initialized")
    return _arq_pool


def get_pubsub_pool() -> aioredis.Redis:
    if _pubsub_pool is None:
        raise RuntimeError("Pub/sub pool not initialized")
    return _pubsub_pool


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """Dependency that yields a Redis connection."""
    pool = get_pubsub_pool()
    yield pool


async def publish_notification(user_id: str, payload: dict) -> None:
    """Publish a notification payload to the user's Redis channel."""
    pool = get_pubsub_pool()
    channel = f"notifications:{user_id}"
    await pool.publish(channel, json.dumps(payload))


async def enqueue_job(function_name: str, **kwargs) -> None:
    """Enqueue a background job via ARQ."""
    pool = get_arq_pool()
    await pool.enqueue_job(function_name, **kwargs)
