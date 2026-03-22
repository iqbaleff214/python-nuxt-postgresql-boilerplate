import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Any

from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TokenType(str, Enum):
    REFRESH = "refresh"
    EMAIL_VERIFY = "email_verify"
    PASSWORD_RESET = "password_reset"
    EMAIL_CHANGE = "email_change"
    DELETE_CANCEL = "delete_cancel"
    MFA_CHALLENGE = "mfa_challenge"
    TOTP_RECOVERY = "totp_recovery"
    MFA_SETUP = "mfa_setup"


def _utcnow():
    return datetime.now(timezone.utc)


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    type: Mapped[TokenType] = mapped_column(
        SAEnum(TokenType, name="tokentype"), nullable=False
    )
    metadata_: Mapped[Optional[Any]] = mapped_column("metadata", JSON, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
