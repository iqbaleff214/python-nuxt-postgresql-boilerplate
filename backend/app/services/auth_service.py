import secrets
import string
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
    encrypt_totp_secret,
)
from app.models.user import User, UserRole, UserStatus
from app.models.token import Token, TokenType


def _err(message: str, status_code: int = 400, errors=None):
    raise HTTPException(
        status_code=status_code,
        detail={"success": False, "message": message, "errors": errors},
    )


def generate_secure_token(length: int = 64) -> str:
    """Generate a cryptographically secure random token."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_recovery_code() -> str:
    """Generate a 10-character alphanumeric recovery code."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(10))


async def create_token_record(
    db: AsyncSession,
    user_id: UUID,
    token_type: TokenType,
    expires_in: timedelta,
    metadata: dict | None = None,
) -> str:
    """Create a token, store its hash in DB, and return the raw token."""
    raw_token = generate_secure_token()
    token_hash = hash_token(raw_token)

    token_record = Token(
        user_id=user_id,
        token=token_hash,
        type=token_type,
        metadata_=metadata,
        expires_at=datetime.now(timezone.utc) + expires_in,
    )
    db.add(token_record)
    await db.flush()
    return raw_token


async def find_and_validate_token(
    db: AsyncSession,
    raw_token: str,
    token_type: TokenType,
) -> Token:
    """Find a token by hash, validate it is not expired or used."""
    token_hash = hash_token(raw_token)
    result = await db.execute(
        select(Token).where(
            Token.token == token_hash,
            Token.type == token_type,
        )
    )
    token = result.scalar_one_or_none()

    if not token:
        _err("Invalid token", 400)

    if token.used_at is not None:
        _err("Token has already been used", 400)

    if token.expires_at < datetime.now(timezone.utc):
        _err("Token has expired", 400)

    return token


async def mark_token_used(db: AsyncSession, token: Token) -> None:
    token.used_at = datetime.now(timezone.utc)
    await db.flush()


async def invalidate_user_tokens(
    db: AsyncSession, user_id: UUID, token_types: list[TokenType]
) -> None:
    """Delete all tokens of specified types for a user."""
    await db.execute(
        delete(Token).where(
            Token.user_id == user_id,
            Token.type.in_(token_types),
        )
    )
    await db.flush()


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
) -> tuple[User, str]:
    """Create a new user and return (user, verify_token)."""
    existing = await db.execute(select(User).where(User.email == email.lower()))
    if existing.scalar_one_or_none():
        _err("A user with this email already exists", 409)

    user = User(
        email=email.lower(),
        hashed_password=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        is_email_verified=False,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    verify_token = await create_token_record(
        db,
        user.id,
        TokenType.EMAIL_VERIFY,
        timedelta(hours=24),
    )
    return user, verify_token


async def verify_email(db: AsyncSession, raw_token: str) -> User:
    """Verify the user's email and return the user."""
    token = await find_and_validate_token(db, raw_token, TokenType.EMAIL_VERIFY)
    result = await db.execute(select(User).where(User.id == token.user_id))
    user = result.scalar_one_or_none()
    if not user:
        _err("User not found", 404)

    user.is_email_verified = True
    await mark_token_used(db, token)
    await db.flush()
    return user


async def resend_verification(db: AsyncSession, email: str) -> tuple[User, str]:
    """Resend verification email; returns (user, new_token)."""
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()
    if not user:
        _err("No user found with that email address", 404)

    if user.is_email_verified:
        _err("Email is already verified", 400)

    # Delete old tokens
    await invalidate_user_tokens(db, user.id, [TokenType.EMAIL_VERIFY])

    new_token = await create_token_record(
        db, user.id, TokenType.EMAIL_VERIFY, timedelta(hours=24)
    )
    return user, new_token


async def login_user(
    db: AsyncSession, email: str, password: str
) -> dict:
    """Authenticate user and return token data or mfa_challenge info."""
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        _err("Invalid email or password", 401)

    if user.status == UserStatus.INACTIVE:
        _err("Your account is inactive. Please contact support.", 403)

    if user.status == UserStatus.BANNED:
        _err("Your account has been banned. Please contact support.", 403)

    if not user.is_email_verified:
        _err("Please verify your email address before logging in.", 403)

    if user.deleted_at is not None:
        _err("This account has been deleted.", 403)

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    if user.is_2fa_enabled:
        challenge_token = await create_token_record(
            db,
            user.id,
            TokenType.MFA_CHALLENGE,
            timedelta(minutes=settings.MFA_CHALLENGE_TOKEN_EXPIRE_MINUTES),
        )
        return {"requires_2fa": True, "mfa_challenge_token": challenge_token}

    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token_raw = create_refresh_token(str(user.id))

    await create_token_record(
        db,
        user.id,
        TokenType.REFRESH,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        metadata={"token": hash_token(refresh_token_raw)},
    )

    return {
        "requires_2fa": False,
        "access_token": access_token,
        "refresh_token": refresh_token_raw,
    }


async def verify_2fa(
    db: AsyncSession, mfa_challenge_token: str, code: str
) -> dict:
    """Verify 2FA code and issue tokens."""
    from app.core.security import decrypt_totp_secret
    from app.services.totp_service import verify_totp

    token = await find_and_validate_token(db, mfa_challenge_token, TokenType.MFA_CHALLENGE)
    result = await db.execute(select(User).where(User.id == token.user_id))
    user = result.scalar_one_or_none()
    if not user:
        _err("User not found", 404)

    await mark_token_used(db, token)

    # Try TOTP first
    if user.totp_secret:
        decrypted = decrypt_totp_secret(user.totp_secret)
        if verify_totp(decrypted, code):
            access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
            refresh_raw = create_refresh_token(str(user.id))
            await create_token_record(
                db,
                user.id,
                TokenType.REFRESH,
                timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                metadata={"token": hash_token(refresh_raw)},
            )
            return {"access_token": access_token, "refresh_token": refresh_raw}

    # Try recovery code
    code_hash = hash_token(code)
    recovery_result = await db.execute(
        select(Token).where(
            Token.user_id == user.id,
            Token.type == TokenType.TOTP_RECOVERY,
            Token.token == code_hash,
            Token.used_at.is_(None),
        )
    )
    recovery_token = recovery_result.scalar_one_or_none()
    if recovery_token:
        await mark_token_used(db, recovery_token)
        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        refresh_raw = create_refresh_token(str(user.id))
        await create_token_record(
            db,
            user.id,
            TokenType.REFRESH,
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            metadata={"token": hash_token(refresh_raw)},
        )
        return {"access_token": access_token, "refresh_token": refresh_raw}

    _err("Invalid 2FA code", 401)


async def refresh_tokens(db: AsyncSession, raw_refresh_token: str) -> dict:
    """Validate refresh token and rotate it."""
    from app.core.security import decode_token

    payload = decode_token(raw_refresh_token)
    user_id = payload.get("sub")
    if not user_id or payload.get("type") != "refresh":
        _err("Invalid refresh token", 401)

    token_hash = hash_token(raw_refresh_token)
    result = await db.execute(
        select(Token).where(
            Token.user_id == UUID(user_id),
            Token.type == TokenType.REFRESH,
            Token.used_at.is_(None),
        )
    )
    tokens = result.scalars().all()

    # Find matching token by comparing hashes stored in metadata
    matching_token = None
    for t in tokens:
        if t.metadata_ and t.metadata_.get("token") == token_hash:
            matching_token = t
            break

    if not matching_token:
        _err("Refresh token not found or already used", 401)

    if matching_token.expires_at < datetime.now(timezone.utc):
        _err("Refresh token has expired", 401)

    # Rotate - mark old as used
    await mark_token_used(db, matching_token)

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        _err("User not found", 404)

    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    new_refresh_raw = create_refresh_token(str(user.id))
    await create_token_record(
        db,
        user.id,
        TokenType.REFRESH,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        metadata={"token": hash_token(new_refresh_raw)},
    )

    return {"access_token": access_token, "refresh_token": new_refresh_raw}


async def logout_user(db: AsyncSession, user_id: UUID, raw_refresh_token: str) -> None:
    """Revoke the refresh token."""
    token_hash = hash_token(raw_refresh_token)
    result = await db.execute(
        select(Token).where(
            Token.user_id == user_id,
            Token.type == TokenType.REFRESH,
            Token.used_at.is_(None),
        )
    )
    tokens = result.scalars().all()
    for t in tokens:
        if t.metadata_ and t.metadata_.get("token") == token_hash:
            await mark_token_used(db, t)
            break


async def forgot_password(db: AsyncSession, email: str) -> tuple[User | None, str | None]:
    """Create a password reset token. Always returns 200 to prevent enumeration."""
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()
    if not user or user.deleted_at is not None:
        return None, None

    # Invalidate old reset tokens
    await invalidate_user_tokens(db, user.id, [TokenType.PASSWORD_RESET])

    reset_token = await create_token_record(
        db, user.id, TokenType.PASSWORD_RESET, timedelta(hours=1)
    )
    return user, reset_token


async def reset_password(db: AsyncSession, raw_token: str, new_password: str) -> User:
    """Reset password using a valid token."""
    token = await find_and_validate_token(db, raw_token, TokenType.PASSWORD_RESET)
    result = await db.execute(select(User).where(User.id == token.user_id))
    user = result.scalar_one_or_none()
    if not user:
        _err("User not found", 404)

    user.hashed_password = hash_password(new_password)
    await mark_token_used(db, token)

    # Invalidate all refresh tokens
    await invalidate_user_tokens(db, user.id, [TokenType.REFRESH])
    await db.flush()
    return user


async def change_password(
    db: AsyncSession, user: User, current_password: str, new_password: str
) -> None:
    """Change password after verifying current password."""
    if not verify_password(current_password, user.hashed_password):
        _err("Current password is incorrect", 400)

    user.hashed_password = hash_password(new_password)
    await invalidate_user_tokens(db, user.id, [TokenType.REFRESH])
    await db.flush()
