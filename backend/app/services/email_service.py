import os
from datetime import datetime
from pathlib import Path
from typing import Any

import aiosmtplib
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"

jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_template(template_name: str, context: dict[str, Any]) -> str:
    template = jinja_env.get_template(template_name)
    # Inject current year for copyright notices
    ctx = {"current_year": datetime.now().year, **context}
    return template.render(**ctx)


async def send_via_smtp(to_email: str, subject: str, html_body: str) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    message["To"] = to_email

    part = MIMEText(html_body, "html")
    message.attach(part)

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER or None,
        password=settings.SMTP_PASS or None,
        use_tls=settings.SMTP_PORT == 465,
        start_tls=settings.SMTP_PORT == 587,
    )


async def send_via_sendgrid(to_email: str, subject: str, html_body: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": settings.MAIL_FROM, "name": settings.MAIL_FROM_NAME},
                "subject": subject,
                "content": [{"type": "text/html", "value": html_body}],
            },
        )
        response.raise_for_status()


async def send_via_resend(to_email: str, subject: str, html_body: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>",
                "to": [to_email],
                "subject": subject,
                "html": html_body,
            },
        )
        response.raise_for_status()


async def send_email(
    to_email: str,
    subject: str,
    template_name: str,
    template_ctx: dict[str, Any],
) -> None:
    """Render template and send via configured mail provider."""
    html_body = render_template(template_name, template_ctx)

    if settings.MAIL_PROVIDER == "smtp":
        await send_via_smtp(to_email, subject, html_body)
    elif settings.MAIL_PROVIDER == "sendgrid":
        await send_via_sendgrid(to_email, subject, html_body)
    elif settings.MAIL_PROVIDER == "resend":
        await send_via_resend(to_email, subject, html_body)
    else:
        raise ValueError(f"Unknown mail provider: {settings.MAIL_PROVIDER}")
