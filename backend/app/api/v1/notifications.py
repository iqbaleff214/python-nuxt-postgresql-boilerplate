from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.notification import NotificationResponse, UnreadCountResponse
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


def ok(data=None, message="Success", meta=None):
    return {"success": True, "message": message, "data": data, "meta": meta}


@router.get("/")
async def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notifications, total = await notification_service.get_notifications(
        db,
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        unread_only=unread_only,
    )
    total_pages = (total + per_page - 1) // per_page

    return ok(
        data=[NotificationResponse.model_validate(n).model_dump() for n in notifications],
        meta={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
        message="Notifications retrieved.",
    )


@router.get("/unread-count")
async def get_unread_count(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await notification_service.get_unread_count(db, current_user.id)
    return ok(data={"count": count}, message="Unread count retrieved.")


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notification = await notification_service.mark_notification_read(
        db, notification_id, current_user.id
    )
    if not notification:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "message": "Notification not found", "errors": None},
        )
    return ok(
        data=NotificationResponse.model_validate(notification).model_dump(),
        message="Notification marked as read.",
    )


@router.patch("/read-all")
async def mark_all_read(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await notification_service.mark_all_notifications_read(db, current_user.id)
    return ok(message="All notifications marked as read.")
