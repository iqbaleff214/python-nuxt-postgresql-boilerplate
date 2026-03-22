import io
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import enqueue_job
from app.core.security import (
    get_current_user,
    encrypt_totp_secret,
    decrypt_totp_secret,
    hash_token,
    verify_password,
)
from app.models.token import Token, TokenType
from app.models.user import User
from app.schemas.auth import (
    Enable2FARequest,
    Disable2FARequest,
    RegenerateCodesRequest,
)
from app.schemas.profile import UpdateProfileRequest, ChangeEmailRequest
from app.schemas.user import UserResponse
from app.services.auth_service import (
    create_token_record,
    find_and_validate_token,
    mark_token_used,
    invalidate_user_tokens,
    generate_recovery_code,
)
from app.services.storage_service import get_storage_service
from app.services import totp_service

router = APIRouter(prefix="/profile", tags=["profile"])

ALLOWED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB


def ok(data=None, message="Success", meta=None):
    return {"success": True, "message": message, "data": data, "meta": meta}


def _err(message: str, status_code: int = 400, errors=None):
    raise HTTPException(
        status_code=status_code,
        detail={"success": False, "message": message, "errors": errors},
    )


@router.get("/me", response_model=None)
async def get_profile(current_user: User = Depends(get_current_user)):
    return ok(
        data=UserResponse.model_validate(current_user).model_dump(),
        message="Profile retrieved.",
    )


@router.patch("/me")
async def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.first_name is not None:
        current_user.first_name = body.first_name.strip()
    if body.last_name is not None:
        current_user.last_name = body.last_name.strip()
    if body.display_name is not None:
        current_user.display_name = body.display_name.strip() or None
    if body.bio is not None:
        current_user.bio = body.bio.strip() or None

    await db.flush()
    await db.refresh(current_user)
    return ok(
        data=UserResponse.model_validate(current_user).model_dump(),
        message="Profile updated.",
    )


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from PIL import Image

    if file.content_type not in ALLOWED_IMAGE_MIMES:
        _err(f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_MIMES)}", 422)

    contents = await file.read()
    if len(contents) > MAX_AVATAR_SIZE:
        _err("File size must not exceed 2MB", 422)

    # Validate it is actually a readable image
    try:
        img = Image.open(io.BytesIO(contents))
        img.verify()
    except Exception:
        _err("Invalid image file", 422)

    ext = (file.content_type or "image/jpeg").split("/")[-1].replace("jpeg", "jpg")
    path = f"avatars/{current_user.id}/{uuid.uuid4()}.{ext}"

    storage = get_storage_service()

    # Delete old avatar if exists
    if current_user.avatar_url and "/static/" in current_user.avatar_url:
        try:
            old_path = current_user.avatar_url.split("/static/")[-1]
            await storage.delete(old_path)
        except Exception:
            pass

    url = await storage.upload(contents, path, file.content_type or "image/jpeg")
    current_user.avatar_url = url
    await db.flush()
    await db.refresh(current_user)

    return ok(data={"avatar_url": url}, message="Avatar uploaded successfully.")


@router.post("/change-email")
async def change_email(
    body: ChangeEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check new email not already taken
    result = await db.execute(
        select(User).where(User.email == body.new_email.lower())
    )
    if result.scalar_one_or_none():
        _err("This email address is already in use", 409)

    # Invalidate old email change tokens
    await invalidate_user_tokens(db, current_user.id, [TokenType.EMAIL_CHANGE])

    change_token = await create_token_record(
        db,
        current_user.id,
        TokenType.EMAIL_CHANGE,
        timedelta(hours=24),
        metadata={"new_email": body.new_email.lower()},
    )

    verify_url = f"{settings.FRONTEND_URL}/verify-email-change?token={change_token}"
    await enqueue_job(
        "send_email",
        to_email=body.new_email,
        subject=f"Verify Your New Email — {settings.APP_NAME}",
        template_name="email_change_verify.html",
        template_ctx={
            "app_name": settings.APP_NAME,
            "first_name": current_user.first_name,
            "verify_url": verify_url,
        },
    )

    return ok(message="A verification link has been sent to your new email address.")


@router.get("/verify-email-change")
async def verify_email_change(token: str, db: AsyncSession = Depends(get_db)):
    token_record = await find_and_validate_token(db, token, TokenType.EMAIL_CHANGE)

    if not token_record.metadata_ or not token_record.metadata_.get("new_email"):
        _err("Invalid token data", 400)

    new_email = token_record.metadata_["new_email"]
    result = await db.execute(select(User).where(User.id == token_record.user_id))
    user = result.scalar_one_or_none()
    if not user:
        _err("User not found", 404)

    user.email = new_email
    await mark_token_used(db, token_record)
    await db.flush()

    await enqueue_job(
        "send_notification",
        user_id=str(user.id),
        type="email_changed",
        title="Email Address Changed",
        body=f"Your email address has been updated to {new_email}.",
    )

    return ok(message="Email address updated successfully.")


@router.post("/delete-account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.deleted_at = datetime.now(timezone.utc)
    await db.flush()

    cancel_token = await create_token_record(
        db, current_user.id, TokenType.DELETE_CANCEL, timedelta(days=30)
    )
    cancel_url = f"{settings.FRONTEND_URL}/cancel-delete?token={cancel_token}"

    await enqueue_job(
        "send_email",
        to_email=current_user.email,
        subject=f"Account Deletion Scheduled — {settings.APP_NAME}",
        template_name="account_deletion_confirm.html",
        template_ctx={
            "app_name": settings.APP_NAME,
            "first_name": current_user.first_name,
            "cancel_url": cancel_url,
        },
    )

    return ok(
        message="Your account has been scheduled for deletion in 30 days. "
                "Check your email for a cancellation link."
    )


@router.get("/cancel-delete")
async def cancel_delete(token: str, db: AsyncSession = Depends(get_db)):
    token_record = await find_and_validate_token(db, token, TokenType.DELETE_CANCEL)
    result = await db.execute(select(User).where(User.id == token_record.user_id))
    user = result.scalar_one_or_none()
    if not user:
        _err("User not found", 404)

    user.deleted_at = None
    await mark_token_used(db, token_record)
    await db.flush()

    return ok(message="Account deletion cancelled. Your account has been restored.")


@router.get("/2fa/setup")
async def setup_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.is_2fa_enabled:
        _err("2FA is already enabled on this account", 400)

    secret = totp_service.generate_secret()
    uri = totp_service.get_totp_uri(secret, current_user.email, settings.APP_NAME)
    qr_code = totp_service.get_qr_code_base64(uri)

    # Encrypt and store the secret temporarily
    encrypted_secret = encrypt_totp_secret(secret)
    await invalidate_user_tokens(db, current_user.id, [TokenType.MFA_SETUP])

    setup_token_raw = await create_token_record(
        db,
        current_user.id,
        TokenType.MFA_SETUP,
        timedelta(minutes=10),
        metadata={"encrypted_secret": encrypted_secret},
    )

    return ok(
        data={
            "setup_token": setup_token_raw,
            "otpauth_uri": uri,
            "qr_code_base64": qr_code,
            "secret": secret,
        },
        message="Scan the QR code with your authenticator app, then confirm with /2fa/enable.",
    )


@router.post("/2fa/enable")
async def enable_2fa(
    body: Enable2FARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.is_2fa_enabled:
        _err("2FA is already enabled on this account", 400)

    token_record = await find_and_validate_token(db, body.setup_token, TokenType.MFA_SETUP)

    if str(token_record.user_id) != str(current_user.id):
        _err("Invalid setup token", 403)

    if not token_record.metadata_ or not token_record.metadata_.get("encrypted_secret"):
        _err("Invalid setup token data", 400)

    encrypted_secret = token_record.metadata_["encrypted_secret"]
    raw_secret = decrypt_totp_secret(encrypted_secret)

    if not totp_service.verify_totp(raw_secret, body.code):
        _err("Invalid TOTP code. Please check your authenticator app.", 400)

    current_user.totp_secret = encrypted_secret
    current_user.is_2fa_enabled = True
    await mark_token_used(db, token_record)

    # Generate 8 recovery codes
    recovery_codes = []
    for _ in range(8):
        code = generate_recovery_code()
        recovery_codes.append(code)
        recovery_token = Token(
            user_id=current_user.id,
            token=hash_token(code),
            type=TokenType.TOTP_RECOVERY,
            expires_at=datetime.now(timezone.utc) + timedelta(days=3650),
        )
        db.add(recovery_token)

    await db.flush()

    return ok(
        data={"recovery_codes": recovery_codes},
        message="2FA enabled successfully. Save these recovery codes — they will not be shown again.",
    )


@router.post("/2fa/disable")
async def disable_2fa(
    body: Disable2FARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.is_2fa_enabled:
        _err("2FA is not currently enabled on this account", 400)

    if not verify_password(body.password, current_user.hashed_password):
        _err("Invalid password", 401)

    if not current_user.totp_secret:
        _err("No TOTP secret found", 400)

    raw_secret = decrypt_totp_secret(current_user.totp_secret)
    if not totp_service.verify_totp(raw_secret, body.code):
        _err("Invalid TOTP code", 401)

    current_user.totp_secret = None
    current_user.is_2fa_enabled = False
    await invalidate_user_tokens(db, current_user.id, [TokenType.TOTP_RECOVERY])
    await db.flush()

    await enqueue_job(
        "send_notification",
        user_id=str(current_user.id),
        type="2fa_disabled",
        title="Two-Factor Authentication Disabled",
        body="2FA has been disabled on your account. If this was not you, contact support immediately.",
    )

    return ok(message="2FA has been disabled successfully.")


@router.post("/2fa/regenerate-codes")
async def regenerate_recovery_codes(
    body: RegenerateCodesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.is_2fa_enabled:
        _err("2FA is not currently enabled on this account", 400)

    if not verify_password(body.password, current_user.hashed_password):
        _err("Invalid password", 401)

    if not current_user.totp_secret:
        _err("No TOTP secret found", 400)

    raw_secret = decrypt_totp_secret(current_user.totp_secret)
    if not totp_service.verify_totp(raw_secret, body.code):
        _err("Invalid TOTP code", 401)

    # Delete old recovery codes and generate fresh ones
    await invalidate_user_tokens(db, current_user.id, [TokenType.TOTP_RECOVERY])

    recovery_codes = []
    for _ in range(8):
        code = generate_recovery_code()
        recovery_codes.append(code)
        recovery_token = Token(
            user_id=current_user.id,
            token=hash_token(code),
            type=TokenType.TOTP_RECOVERY,
            expires_at=datetime.now(timezone.utc) + timedelta(days=3650),
        )
        db.add(recovery_token)

    await db.flush()

    return ok(
        data={"recovery_codes": recovery_codes},
        message="Recovery codes regenerated. Save these in a safe place.",
    )
