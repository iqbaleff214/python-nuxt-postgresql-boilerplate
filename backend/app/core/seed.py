import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus

logger = logging.getLogger(__name__)


async def seed_superadmin() -> None:
    """Ensure a default superadmin user exists. Idempotent — safe to call every startup."""
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(
            select(User).where(User.email == settings.SUPERADMIN_EMAIL)
        )
        if existing:
            return

        admin = User(
            email=settings.SUPERADMIN_EMAIL,
            hashed_password=hash_password(settings.SUPERADMIN_PASSWORD),
            first_name=settings.SUPERADMIN_FIRST_NAME,
            last_name=settings.SUPERADMIN_LAST_NAME,
            role=UserRole.SUPERADMIN,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
        )
        session.add(admin)
        await session.commit()
        logger.info("Default superadmin created: %s", settings.SUPERADMIN_EMAIL)
