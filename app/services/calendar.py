"""Calendar booking links (Cal.com / Bitrix24 calendar).

Booking links carry the tenant and locale plus any UTM attribution so a scheduled
call is attributed to the same campaign as the assessment that produced it.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode


@dataclass(slots=True, frozen=True)
class BookingLink:
    """A provider booking URL for one event type."""

    provider: str
    url: str


def calcom_link(
    base_url: str,
    event_type: str,
    *,
    tenant: str,
    locale: str,
    utm: dict[str, str] | None = None,
) -> BookingLink:
    """Build a Cal.com booking link with tenant/locale and optional UTM params."""
    if not base_url or not event_type:
        raise ValueError("base_url and event_type are required")
    params: dict[str, str] = {"tenant": tenant, "locale": locale}
    if utm:
        params.update({key: value for key, value in utm.items() if value})
    url = f"{base_url.rstrip('/')}/{event_type}?{urlencode(params)}"
    return BookingLink(provider="calcom", url=url)
