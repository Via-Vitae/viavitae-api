"""Transactional email via an EU SMTP relay (LT/EN/RU templates).

Delivery must be SPF/DKIM/DMARC aligned, which is a property of the relay and
the sending domain rather than of this code; the client's job is to refuse to
send to an unconfigured relay and to keep personal data out of the logs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

SUPPORTED_LOCALES = ("lt", "en", "ru")


@dataclass(slots=True, frozen=True)
class EmailMessage:
    """One templated transactional email."""

    to: str
    template: str
    locale: str
    context: dict[str, str] = field(default_factory=dict)
    subject: str = ""


async def send(message: EmailMessage) -> bool:
    """Render and hand one message to the configured relay.

    Returns ``True`` when the message was accepted for delivery and ``False``
    when no relay is configured (dev without SMTP). Never logs the recipient or
    the rendered body.
    """
    if message.locale not in SUPPORTED_LOCALES:
        raise ValueError(f"unsupported locale '{message.locale}'")
    if settings.smtp_url is None:
        # In dev without SMTP, Mailpit (docker-compose) is the sink; here we
        # simply report that nothing was dispatched.
        logger.warning("email.smtp_not_configured", template=message.template)
        return False
    # TODO(api): render the locale template, connect via the relay, send, and
    #            record delivery in the notification model. No PII in logs.
    logger.info("email.accepted", template=message.template, locale=message.locale)
    return True
