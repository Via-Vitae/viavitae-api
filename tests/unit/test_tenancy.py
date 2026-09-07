"""Tenant resolution and schema mapping (ADR-004)."""

from __future__ import annotations

import pytest
from app.core.tenancy import (
    InvalidTenantError,
    TenantContext,
    resolve_tenant,
    schema_for,
    subdomain_of,
)


def test_schema_for_maps_slug_and_normalises_hyphens() -> None:
    assert schema_for("anne") == "tenant_anne"
    assert schema_for("st-anne") == "tenant_st_anne"


@pytest.mark.parametrize("slug", ["", "UPPER", "bad slug", "../evil", "-lead", "a" * 64])
def test_schema_for_rejects_unsafe_slugs(slug: str) -> None:
    """Hostile or malformed slugs never become a schema name."""
    with pytest.raises(InvalidTenantError):
        schema_for(slug)


@pytest.mark.parametrize(
    ("host", "expected"),
    [
        ("anne.api.viavitae.eu", "anne"),
        ("anne.api.viavitae.eu:8000", "anne"),
        ("api.viavitae.eu", None),
        ("viavitae.eu", None),
        ("localhost", None),
        ("example.com", None),
    ],
)
def test_subdomain_extraction(host: str, expected: str | None) -> None:
    assert subdomain_of(host) == expected


def test_resolve_tenant_prefers_jwt_claim_over_host() -> None:
    ctx = resolve_tenant(jwt_claim="Bob", host="anne.api.viavitae.eu")
    assert isinstance(ctx, TenantContext)
    assert ctx.slug == "bob"
    assert ctx.schema == "tenant_bob"


def test_resolve_tenant_falls_back_to_subdomain() -> None:
    assert resolve_tenant(host="anne.api.viavitae.eu").slug == "anne"


def test_resolve_tenant_without_any_signal_is_rejected() -> None:
    with pytest.raises(InvalidTenantError):
        resolve_tenant()
