"""Authorisation seam: the tenant comes from context, never the request body."""

from __future__ import annotations

import pytest
from app.api.deps import get_current_tenant
from app.core.tenancy import InvalidTenantError
from httpx import AsyncClient
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


@pytest.mark.parametrize("environment", ["staging", "prod"])
@pytest.mark.parametrize("claim", [None, "", "   ", 123])
async def test_non_development_rejects_unverified_tenant(
    environment: str,
    claim: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.config import settings
    from app.core.errors import ApiError

    monkeypatch.setattr(settings, "environment", environment)
    request = _request("anne.api.viavitae.eu")
    request.state.tenant_claim = claim
    with pytest.raises(ApiError) as exc:
        get_current_tenant(request, "bob")
    assert exc.value.status_code == 401
    assert exc.value.code == "authentication_required"


@pytest.mark.parametrize("environment", ["staging", "prod"])
def test_non_development_uses_only_trusted_claim(
    environment: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.config import settings

    monkeypatch.setattr(settings, "environment", environment)
    request = _request("anne.api.viavitae.eu")
    request.state.tenant_claim = "trusted"
    assert get_current_tenant(request, "attacker").slug == "trusted"


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/v1/ai/audit"),
        ("GET", "/v1/ai/drafts/d1"),
        ("POST", "/v1/ai/drafts"),
        ("POST", "/v1/ai/drafts/d1/decision"),
    ],
)
async def test_production_tenant_route_returns_401_envelope(
    client: AsyncClient,
    method: str,
    path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.config import settings

    monkeypatch.setattr(settings, "environment", "prod")
    response = await client.request(method, path, headers={"X-Tenant": "anne"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_required"
