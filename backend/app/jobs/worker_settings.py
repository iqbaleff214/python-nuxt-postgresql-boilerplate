import logging

import redis.asyncio as aioredis
from arq.connections import RedisSettings
from arq.cron import cron

from app.core.config import settings
from app.jobs.email_jobs import send_email
from app.jobs.notification_jobs import send_notification, broadcast_announcement
from app.jobs.maintenance_jobs import cleanup_expired_tokens, hard_delete_accounts

logger = logging.getLogger(__name__)


async def startup(ctx: dict) -> None:
    """Initialize shared resources for the ARQ worker."""
    ctx["redis"] = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    logger.info("ARQ worker started.")


async def shutdown(ctx: dict) -> None:
    """Cleanup shared resources."""
    redis_client = ctx.get("redis")
    if redis_client:
        await redis_client.aclose()
    logger.info("ARQ worker shut down.")


class WorkerSettings:
    functions = [
        send_email,
        send_notification,
        broadcast_announcement,
        cleanup_expired_tokens,
        hard_delete_accounts,
    ]
    cron_jobs = [
        cron(cleanup_expired_tokens, hour={0}, minute={0}),  # daily at midnight
        cron(hard_delete_accounts, hour={1}, minute={0}),    # daily at 1am
    ]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10
    job_timeout = 300  # 5 minutes
