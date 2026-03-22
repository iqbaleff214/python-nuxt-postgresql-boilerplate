from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import enqueue_job
from app.core.security import require_role
from app.models.user import UserRole, UserStatus
from app.schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UpdateUserStatusRequest,
    UserResponse,
)
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])

superadmin_dep = require_role(UserRole.SUPERADMIN)


def ok(data=None, message="Success", meta=None):
    return {"success": True, "message": message, "data": data, "meta": meta}


@router.get("/")
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[UserRole] = Query(None),
    status: Optional[UserStatus] = Query(None),
    is_email_verified: Optional[bool] = Query(None),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc"),
    acting_user=Depends(superadmin_dep),
    db: AsyncSession = Depends(get_db),
):
    users, total = await user_service.get_users(
        db,
        page=page,
        per_page=per_page,
        search=search,
        role=role,
        status=status,
        is_email_verified=is_email_verified,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    total_pages = (total + per_page - 1) // per_page

    return ok(
        data=[UserResponse.model_validate(u).model_dump() for u in users],
        meta={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
        message="Users retrieved.",
    )


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    acting_user=Depends(superadmin_dep),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user_by_id(db, user_id)
    return ok(data=UserResponse.model_validate(user).model_dump(), message="User retrieved.")


@router.post("/", status_code=201)
async def create_user(
    body: CreateUserRequest,
    acting_user=Depends(superadmin_dep),
    db: AsyncSession = Depends(get_db),
):
    user, temp_password = await user_service.create_user_by_admin(db, body)
    set_password_url = f"{settings.FRONTEND_URL}/set-password?email={user.email}"

    await enqueue_job(
        "send_email",
        to_email=user.email,
        subject=f"Your account on {settings.APP_NAME} has been created",
        template_name="new_account_by_admin.html",
        template_ctx={
            "app_name": settings.APP_NAME,
            "first_name": user.first_name,
            "set_password_url": set_password_url,
            "temp_password": temp_password,
        },
    )

    return ok(
        data=UserResponse.model_validate(user).model_dump(),
        message="User created successfully.",
    )


@router.patch("/{user_id}")
async def update_user(
    user_id: UUID,
    body: UpdateUserRequest,
    acting_user=Depends(superadmin_dep),
    db: AsyncSession = Depends(get_db),
):
    target_user = await user_service.get_user_by_id(db, user_id)
    updated = await user_service.update_user(db, target_user, acting_user, body)
    return ok(
        data=UserResponse.model_validate(updated).model_dump(),
        message="User updated.",
    )


@router.patch("/{user_id}/status")
async def update_user_status(
    user_id: UUID,
    body: UpdateUserStatusRequest,
    acting_user=Depends(superadmin_dep),
    db: AsyncSession = Depends(get_db),
):
    target_user = await user_service.get_user_by_id(db, user_id)
    updated = await user_service.update_user_status(db, target_user, acting_user, body)

    # Send appropriate email
    if body.status == UserStatus.BANNED:
        await enqueue_job(
            "send_email",
            to_email=updated.email,
            subject=f"Your account has been banned — {settings.APP_NAME}",
            template_name="account_banned.html",
            template_ctx={
                "app_name": settings.APP_NAME,
                "first_name": updated.first_name,
                "reason": body.ban_reason or "Violation of terms of service",
            },
        )
        await enqueue_job(
            "send_notification",
            user_id=str(updated.id),
            type="account_banned",
            title="Account Banned",
            body=f"Your account has been banned. Reason: {body.ban_reason or 'Violation of terms of service'}",
        )
    elif body.status == UserStatus.INACTIVE:
        await enqueue_job(
            "send_email",
            to_email=updated.email,
            subject=f"Your account has been deactivated — {settings.APP_NAME}",
            template_name="account_deactivated.html",
            template_ctx={
                "app_name": settings.APP_NAME,
                "first_name": updated.first_name,
            },
        )
        await enqueue_job(
            "send_notification",
            user_id=str(updated.id),
            type="account_deactivated",
            title="Account Deactivated",
            body="Your account has been deactivated. Please contact support.",
        )

    return ok(
        data=UserResponse.model_validate(updated).model_dump(),
        message="User status updated.",
    )


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    acting_user=Depends(superadmin_dep),
    db: AsyncSession = Depends(get_db),
):
    target_user = await user_service.get_user_by_id(db, user_id)
    await user_service.hard_delete_user(db, target_user, acting_user)
    return None
