import logging
from typing import Any

from app.services.email_service import send_email as _send_email

logger = logging.getLogger(__name__)


async def send_email(
    ctx: dict,
    *,
    to_email: str,
    subject: str,
    template_name: str,
    template_ctx: dict[str, Any],
) -> None:
    """ARQ job: render a Jinja2 template and send an email via the configured provider."""
    try:
        await _send_email(
            to_email=to_email,
            subject=subject,
            template_name=template_name,
            template_ctx=template_ctx,
        )
        logger.info("Email sent to %s: %s", to_email, subject)
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc, exc_info=True)
        raise
