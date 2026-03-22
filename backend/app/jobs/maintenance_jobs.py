import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import delete, and_, or_

from app.core.database import AsyncSessionLocal
from app.models.token import Token
from app.models.user import User

logger = logging.getLogger(__name__)


async def cleanup_expired_tokens(ctx: dict) -> None:
    """Daily job: remove expired tokens and tokens used more than 7 days ago."""
    try:
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                delete(Token).where(
                    or_(
                        Token.expires_at < now,
                        and_(
                            Token.used_at.is_not(None),
                            Token.created_at < seven_days_ago,
                        ),
                    )
                )
            )
            await db.commit()
            logger.info("Cleaned up %d expired/used tokens", result.rowcount)
    except Exception as exc:
        logger.error("Failed to clean up tokens: %s", exc, exc_info=True)
        raise


async def hard_delete_accounts(ctx: dict) -> None:
    """Daily job: permanently delete accounts soft-deleted more than 30 days ago."""
    try:
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                delete(User).where(
                    and_(
                        User.deleted_at.is_not(None),
                        User.deleted_at < thirty_days_ago,
                    )
                )
            )
            await db.commit()
            logger.info("Hard deleted %d accounts scheduled for removal", result.rowcount)
    except Exception as exc:
        logger.error("Failed to hard delete accounts: %s", exc, exc_info=True)
        raise
