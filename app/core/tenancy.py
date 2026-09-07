"""Tenant resolution and isolation context (ADR-004).

A tenant is identified from the authenticated context -- a JWT claim first, the
subdomain as a fallback -- never from a request body field, so a client cannot
address another tenant's data by editing a payload. Resolution yields a
``TenantContext`` carrying the tenant slug and its PostgreSQL schema; the
row-level-security session variable is set in ``app.db.session.get_session``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.errors import ApiError

# A DNS-safe slug: lowercase alphanumeric with inner hyphens, 1-63 characters.
_SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
_RESERVED_LABELS = frozenset({"api", "www", "admin", "mail", "cdn"})
_SCHEMA_PREFIX = "tenant_"
_MAX_PG_IDENTIFIER = 63
_DEFAULT_BASE_DOMAIN = "viavitae.eu"


class InvalidTenantError(ApiError):
    """Raised when a tenant cannot be resolved or its slug is not schema-safe."""

    def __init__(self, detail: str) -> None:
        super().__init__("invalid_tenant", detail, status_code=400)


@dataclass(slots=True, frozen=True)
class TenantContext:
    """The resolved tenant for one request."""

    slug: str
    schema: str
    locale: str = "lt"


def schema_for(slug: str) -> str:
    """Map a validated tenant slug to its PostgreSQL schema name."""
    if not _SLUG_RE.match(slug):
        raise InvalidTenantError(f"'{slug}' is not a valid tenant slug")
    schema = f"{_SCHEMA_PREFIX}{slug.replace('-', '_')}"
    if len(schema) > _MAX_PG_IDENTIFIER:
        raise InvalidTenantError("tenant slug is too long for a schema identifier")
    return schema


def subdomain_of(host: str | None, *, base_domain: str = _DEFAULT_BASE_DOMAIN) -> str | None:
    """Extract the tenant subdomain from a Host header, or ``None``.

    ``anne.api.viavitae.eu`` -> ``anne``; ``api.viavitae.eu`` and ``localhost``
    -> ``None``. Reserved labels are never treated as tenant slugs.
    """
    if not host:
        return None
    hostname = host.split(":", 1)[0].strip().lower()
    suffix = f".{base_domain}"
    if not hostname.endswith(suffix):
        return None
    prefix = hostname[: -len(suffix)]
    if not prefix:
        return None
    label = prefix.split(".", 1)[0]
    if not label or label in _RESERVED_LABELS:
        return None
    return label


def resolve_tenant(*, jwt_claim: str | None = None, host: str | None = None) -> TenantContext:
    """Resolve the tenant from the JWT claim first, then the subdomain.

    The slug is always validated by :func:`schema_for`, so a hostile claim such
    as ``../public`` is rejected rather than turned into a schema name.
    """
    slug = (jwt_claim or "").strip().lower() or (subdomain_of(host) or "")
    if not slug:
        raise InvalidTenantError("no tenant could be resolved from the request")
    return TenantContext(slug=slug, schema=schema_for(slug))
