from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    user_id: str | UUID,
    type: str,
    title: str,
    body: str | None = None,
) -> Notification:
    """Create and persist a notification record."""
    notification = Notification(
        user_id=UUID(str(user_id)),
        type=type,
        title=title,
        body=body,
    )
    db.add(notification)
    await db.flush()
    await db.refresh(notification)
    return notification


async def get_notifications(
    db: AsyncSession,
    user_id: UUID,
    page: int = 1,
    per_page: int = 20,
    unread_only: bool = False,
) -> tuple[list[Notification], int]:
    """Return paginated notifications and total count."""
    query = select(Notification).where(Notification.user_id == user_id)
    count_query = select(func.count()).select_from(Notification).where(
        Notification.user_id == user_id
    )

    if unread_only:
        query = query.where(Notification.read_at.is_(None))
        count_query = count_query.where(Notification.read_at.is_(None))

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = (
        query.order_by(Notification.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    notifications = list(result.scalars().all())

    return notifications, total


async def get_unread_count(db: AsyncSession, user_id: UUID) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user_id, Notification.read_at.is_(None))
    )
    return result.scalar_one()


async def mark_notification_read(
    db: AsyncSession, notification_id: UUID, user_id: UUID
) -> Notification | None:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )
    notification = result.scalar_one_or_none()
    if notification and notification.read_at is None:
        notification.read_at = datetime.now(timezone.utc)
        await db.flush()
    return notification


async def mark_all_notifications_read(db: AsyncSession, user_id: UUID) -> None:
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.read_at.is_(None))
        .values(read_at=datetime.now(timezone.utc))
    )
    await db.flush()
