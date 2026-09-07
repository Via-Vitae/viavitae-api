"""Authorisation seam: the tenant comes from context, never the request body."""

from __future__ import annotations

import pytest
from app.api.deps import get_current_tenant
from app.core.tenancy import InvalidTenantError
from starlette.requests import Request


def _request(host: str) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/v1/health",
        "headers": [(b"host", host.encode())],
        "query_string": b"",
        "scheme": "http",
    }
    return Request(scope)


def test_tenant_is_resolved_from_the_request_host() -> None:
    ctx = get_current_tenant(_request("anne.api.viavitae.eu"), None)
    assert ctx.slug == "anne"
    assert ctx.schema == "tenant_anne"


def test_explicit_tenant_claim_wins_over_the_host() -> None:
    ctx = get_current_tenant(_request("api.viavitae.eu"), "bob")
    assert ctx.slug == "bob"


def test_unresolvable_tenant_is_rejected() -> None:
    """No claim and a reserved host label means no tenant can be resolved."""
    with pytest.raises(InvalidTenantError):
        get_current_tenant(_request("api.viavitae.eu"), None)
