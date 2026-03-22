import json
import logging
from typing import Optional

from app.core.database import AsyncSessionLocal
from app.services.notification_service import create_notification

logger = logging.getLogger(__name__)


async def send_notification(
    ctx: dict,
    *,
    user_id: str,
    type: str,
    title: str,
    body: Optional[str] = None,
) -> None:
    """ARQ job: insert a notification and publish to Redis pub/sub."""
    try:
        async with AsyncSessionLocal() as db:
            notification = await create_notification(db, user_id, type, title, body)
            await db.commit()

        # Publish to Redis so connected WebSocket clients receive it immediately
        redis_client = ctx.get("redis")
        if redis_client:
            payload = {
                "type": "notification",
                "id": str(notification.id),
                "notification_type": type,
                "title": title,
                "body": body,
                "created_at": notification.created_at.isoformat(),
            }
            channel = f"notifications:{user_id}"
            await redis_client.publish(channel, json.dumps(payload))

        logger.info("Notification sent to user %s: %s", user_id, title)
    except Exception as exc:
        logger.error(
            "Failed to send notification to user %s: %s", user_id, exc, exc_info=True
        )
        raise


async def broadcast_announcement(
    ctx: dict,
    *,
    title: str,
    body: str,
    user_ids: list[str],
) -> None:
    """ARQ job: send a notification to multiple users."""
    try:
        async with AsyncSessionLocal() as db:
            for user_id in user_ids:
                await create_notification(db, user_id, "announcement", title, body)
            await db.commit()

        redis_client = ctx.get("redis")
        if redis_client:
            payload = {
                "type": "notification",
                "notification_type": "announcement",
                "title": title,
                "body": body,
            }
            for user_id in user_ids:
                channel = f"notifications:{user_id}"
                await redis_client.publish(channel, json.dumps(payload))

        logger.info("Broadcast sent to %d users: %s", len(user_ids), title)
    except Exception as exc:
        logger.error("Failed to broadcast announcement: %s", exc, exc_info=True)
        raise
