from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Literal, Optional

from app.api.v1 import auth, profile, users, notifications
from app.core.config import settings
from app.core.database import get_db
from app.core.redis import enqueue_job
from app.core.security import require_role
from app.models.user import UserRole
from app.schemas.profile import BroadcastRequest
from pydantic import BaseModel


class AnnouncementRequest(BaseModel):
    title: str
    message: str
    target_role: Optional[Literal["user", "admin", "superadmin"]] = None

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth.router)
v1_router.include_router(profile.router)
v1_router.include_router(users.router)
v1_router.include_router(notifications.router)


def ok(data=None, message="Success", meta=None):
    return {"success": True, "message": message, "data": data, "meta": meta}


@v1_router.post("/admin/broadcast", tags=["admin"])
async def broadcast_announcement(
    body: BroadcastRequest,
    acting_user=Depends(require_role(UserRole.SUPERADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Broadcast an announcement to all users."""
    from sqlalchemy import select
    from app.models.user import User

    result = await db.execute(
        select(User.id).where(User.deleted_at.is_(None))
    )
    user_ids = [str(row[0]) for row in result.fetchall()]

    await enqueue_job(
        "broadcast_announcement",
        title=body.title,
        body=body.body,
        user_ids=user_ids,
    )

    return ok(message=f"Broadcast queued for {len(user_ids)} users.")


@v1_router.post("/admin/announcements", tags=["admin"])
async def send_announcement(
    body: AnnouncementRequest,
    acting_user=Depends(require_role(UserRole.SUPERADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Send an announcement notification to all users or filtered by role."""
    from sqlalchemy import select
    from app.models.user import User

    query = select(User.id).where(User.deleted_at.is_(None))
    if body.target_role:
        query = query.where(User.role == body.target_role)

    result = await db.execute(query)
    user_ids = [str(row[0]) for row in result.fetchall()]

    await enqueue_job(
        "broadcast_announcement",
        title=body.title,
        body=body.message,
        user_ids=user_ids,
    )

    return ok(message=f"Announcement queued for {len(user_ids)} users.")
