import secrets
import string
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus
from app.models.token import Token, TokenType
from app.schemas.user import CreateUserRequest, UpdateUserRequest, UpdateUserStatusRequest


def _err(message: str, status_code: int = 400, errors=None):
    raise HTTPException(
        status_code=status_code,
        detail={"success": False, "message": message, "errors": errors},
    )


def generate_temp_password(length: int = 16) -> str:
    """Generate a random temporary password."""
    chars = string.ascii_letters + string.digits + "!@#$%"
    password = (
        secrets.choice(string.ascii_uppercase)
        + secrets.choice(string.digits)
        + "".join(secrets.choice(chars) for _ in range(length - 2))
    )
    lst = list(password)
    secrets.SystemRandom().shuffle(lst)
    return "".join(lst)


async def get_users(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
    role: UserRole | None = None,
    status: UserStatus | None = None,
    is_email_verified: bool | None = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
) -> tuple[list[User], int]:
    """Return paginated users list and total count."""
    query = select(User).where(User.deleted_at.is_(None))
    count_query = select(func.count()).select_from(User).where(User.deleted_at.is_(None))

    if search:
        pattern = f"%{search}%"
        search_filter = or_(
            User.email.ilike(pattern),
            User.first_name.ilike(pattern),
            User.last_name.ilike(pattern),
            User.display_name.ilike(pattern),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if role:
        query = query.where(User.role == role)
        count_query = count_query.where(User.role == role)

    if status:
        query = query.where(User.status == status)
        count_query = count_query.where(User.status == status)

    if is_email_verified is not None:
        query = query.where(User.is_email_verified == is_email_verified)
        count_query = count_query.where(User.is_email_verified == is_email_verified)

    # Sorting
    allowed_sort = {
        "created_at": User.created_at,
        "updated_at": User.updated_at,
        "email": User.email,
        "first_name": User.first_name,
        "last_name": User.last_name,
    }
    sort_col = allowed_sort.get(sort_by, User.created_at)
    if sort_dir == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(query.offset((page - 1) * per_page).limit(per_page))
    users = list(result.scalars().all())

    return users, total


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        _err("User not found", 404)
    return user


async def create_user_by_admin(
    db: AsyncSession, data: CreateUserRequest
) -> tuple[User, str]:
    """Create a user with a temporary password. Returns (user, temp_password)."""
    existing = await db.execute(select(User).where(User.email == data.email.lower()))
    if existing.scalar_one_or_none():
        _err("A user with this email already exists", 409)

    temp_password = generate_temp_password()
    user = User(
        email=data.email.lower(),
        hashed_password=hash_password(temp_password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role,
        status=UserStatus.ACTIVE,
        is_email_verified=True,  # Admin-created accounts are pre-verified
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user, temp_password


async def update_user(
    db: AsyncSession,
    target_user: User,
    acting_user: User,
    data: UpdateUserRequest,
) -> User:
    """Update a user's details with role-change restrictions."""
    # Cannot change own role
    if data.role is not None and target_user.id == acting_user.id:
        _err("Cannot change your own role", 403)

    # Cannot change another superadmin's role
    if (
        data.role is not None
        and target_user.role == UserRole.SUPERADMIN
        and target_user.id != acting_user.id
    ):
        _err("Cannot change a superadmin's role", 403)

    if data.first_name is not None:
        target_user.first_name = data.first_name
    if data.last_name is not None:
        target_user.last_name = data.last_name
    if data.display_name is not None:
        target_user.display_name = data.display_name
    if data.bio is not None:
        target_user.bio = data.bio
    if data.role is not None:
        target_user.role = data.role

    await db.flush()
    await db.refresh(target_user)
    return target_user


async def update_user_status(
    db: AsyncSession,
    target_user: User,
    acting_user: User,
    data: UpdateUserStatusRequest,
) -> User:
    """Update user status with restrictions."""
    if target_user.id == acting_user.id:
        _err("Cannot change your own account status", 403)

    if target_user.role == UserRole.SUPERADMIN:
        _err("Cannot change status of a superadmin account", 403)

    target_user.status = data.status
    await db.flush()
    await db.refresh(target_user)
    return target_user


async def hard_delete_user(
    db: AsyncSession, target_user: User, acting_user: User
) -> None:
    """Permanently delete a user account."""
    if target_user.id == acting_user.id:
        _err("Cannot delete your own account through admin endpoint", 403)

    if target_user.role == UserRole.SUPERADMIN:
        _err("Cannot delete a superadmin account", 403)

    await db.delete(target_user)
    await db.flush()
