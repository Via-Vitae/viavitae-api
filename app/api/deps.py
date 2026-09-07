"""Shared FastAPI dependencies.

This module is the sanctioned seam between the HTTP layer and everything else:
database sessions, the resolved tenant, authentication and the idempotency key.
Routers depend on these instead of importing models or the database directly --
a boundary enforced by the import-linter contract in ``pyproject.toml`` (the
contract scopes the prohibition to ``app.api.v1`` and allows indirect imports, so
``router -> deps -> db`` is fine while a router importing ``app.db`` is not).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenancy import TenantContext, resolve_tenant
from app.db.session import get_session, ping


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield a tenant-scoped database session (see :func:`app.db.session.get_session`)."""
    async for session in get_session():
        yield session


async def database_ready() -> bool:
    """Readiness signal: one round-trip to PostgreSQL, via the db seam."""
    return await ping()


def get_current_tenant(
    request: Request,
    x_tenant: str | None = Header(default=None, alias="X-Tenant"),
) -> TenantContext:
    """Resolve the tenant from the authenticated context, never from the body.

    An unresolvable tenant raises ``InvalidTenantError`` which the error handlers
    render as a 400 envelope.
    """
    # TODO(api): prefer a verified Keycloak JWT claim over the header/subdomain;
    #            the X-Tenant header is a dev fallback and must be disabled in prod.
    claim: str | None = getattr(request.state, "tenant_claim", None)
    return resolve_tenant(jwt_claim=claim or x_tenant, host=request.url.hostname)


def get_idempotency_key(
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> str | None:
    """Extract the client idempotency key for money-moving mutations (ADR-005)."""
    return idempotency_key


SessionDep = Annotated[AsyncSession, Depends(get_db)]
TenantDep = Annotated[TenantContext, Depends(get_current_tenant)]
IdempotencyDep = Annotated[str | None, Depends(get_idempotency_key)]
