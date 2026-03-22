from datetime import timedelta

from fastapi import APIRouter, Depends, Request, Response, Cookie
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import enqueue_job
from app.core.security import limiter, get_current_user
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    Verify2FARequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def ok(data=None, message="Success", meta=None):
    return {"success": True, "message": message, "data": data, "meta": meta}


def _set_refresh_cookie(response: Response, token: str, is_prod: bool) -> None:
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",
    )


@router.post("/register", status_code=201)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    user, verify_token = await auth_service.register_user(
        db, body.email, body.password, body.first_name, body.last_name
    )
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={verify_token}"

    await enqueue_job(
        "send_email",
        to_email=user.email,
        subject=f"Welcome to {settings.APP_NAME} — Verify Your Email",
        template_name="welcome_verify.html",
        template_ctx={
            "app_name": settings.APP_NAME,
            "first_name": user.first_name,
            "verify_url": verify_url,
        },
    )

    return ok(
        data={"id": str(user.id), "email": user.email, "first_name": user.first_name},
        message="Registration successful. Please check your email to verify your account.",
    )


@router.post("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    user = await auth_service.verify_email(db, token)

    await enqueue_job(
        "send_email",
        to_email=user.email,
        subject=f"Email Verified — {settings.APP_NAME}",
        template_name="email_verified.html",
        template_ctx={"app_name": settings.APP_NAME, "first_name": user.first_name},
    )

    return ok(message="Email verified successfully. You can now log in.")


@router.post("/resend-verification")
@limiter.limit("3/minute")
async def resend_verification(
    request: Request,
    body: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    user, new_token = await auth_service.resend_verification(db, body.email)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={new_token}"

    await enqueue_job(
        "send_email",
        to_email=user.email,
        subject=f"Verify Your Email — {settings.APP_NAME}",
        template_name="welcome_verify.html",
        template_ctx={
            "app_name": settings.APP_NAME,
            "first_name": user.first_name,
            "verify_url": verify_url,
        },
    )

    return ok(message="Verification email sent. Please check your inbox.")


@router.post("/login")
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    from app.core.redis import get_pubsub_pool

    redis_client = get_pubsub_pool()
    lock_key = f"login_lockout:{body.email.lower()}"
    attempt_key = f"login_attempts:{body.email.lower()}"

    # Check lockout
    locked = await redis_client.get(lock_key)
    if locked:
        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "message": "Too many failed login attempts. Please try again in 15 minutes.",
                "errors": None,
            },
        )

    try:
        result = await auth_service.login_user(db, body.email, body.password)
        # Reset attempts on success
        await redis_client.delete(attempt_key)
        await redis_client.delete(lock_key)
    except HTTPException as exc:
        if exc.status_code == 401:
            # Track failed attempt
            attempts = await redis_client.incr(attempt_key)
            await redis_client.expire(attempt_key, 900)  # 15 min window
            if int(attempts) >= 5:
                await redis_client.set(lock_key, "1", ex=900)
        raise

    if result.get("requires_2fa"):
        return ok(
            data={
                "requires_2fa": True,
                "mfa_challenge_token": result["mfa_challenge_token"],
            },
            message="2FA verification required.",
        )

    is_prod = settings.APP_ENV == "production"
    _set_refresh_cookie(response, result["refresh_token"], is_prod)

    return ok(
        data={"access_token": result["access_token"], "token_type": "bearer"},
        message="Login successful.",
    )


@router.post("/verify-2fa")
async def verify_2fa(
    body: Verify2FARequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await auth_service.verify_2fa(db, body.mfa_challenge_token, body.code)
    is_prod = settings.APP_ENV == "production"
    _set_refresh_cookie(response, result["refresh_token"], is_prod)

    return ok(
        data={"access_token": result["access_token"], "token_type": "bearer"},
        message="2FA verified. Login successful.",
    )


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if refresh_token:
        await auth_service.logout_user(db, current_user.id, refresh_token)

    response.delete_cookie("refresh_token", path="/api/v1/auth")
    return ok(message="Logged out successfully.")


@router.post("/refresh")
async def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail={"success": False, "message": "Refresh token not found", "errors": None},
        )

    result = await auth_service.refresh_tokens(db, refresh_token)
    is_prod = settings.APP_ENV == "production"
    _set_refresh_cookie(response, result["refresh_token"], is_prod)

    return ok(
        data={"access_token": result["access_token"], "token_type": "bearer"},
        message="Token refreshed.",
    )


@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    user, reset_token = await auth_service.forgot_password(db, body.email)

    if user and reset_token:
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        await enqueue_job(
            "send_email",
            to_email=user.email,
            subject=f"Reset Your Password — {settings.APP_NAME}",
            template_name="password_reset.html",
            template_ctx={
                "app_name": settings.APP_NAME,
                "first_name": user.first_name,
                "reset_url": reset_url,
            },
        )

    return ok(
        message="If an account with that email exists, you will receive a password reset link."
    )


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.reset_password(db, body.token, body.new_password)

    await enqueue_job(
        "send_email",
        to_email=user.email,
        subject=f"Your Password Has Been Changed — {settings.APP_NAME}",
        template_name="password_changed.html",
        template_ctx={"app_name": settings.APP_NAME, "first_name": user.first_name},
    )

    return ok(message="Password reset successfully. You can now log in.")


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.change_password(
        db, current_user, body.current_password, body.new_password
    )

    await enqueue_job(
        "send_email",
        to_email=current_user.email,
        subject=f"Your Password Has Been Changed — {settings.APP_NAME}",
        template_name="password_changed.html",
        template_ctx={
            "app_name": settings.APP_NAME,
            "first_name": current_user.first_name,
        },
    )

    return ok(message="Password changed successfully.")
