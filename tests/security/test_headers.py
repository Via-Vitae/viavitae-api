"""Security header hardening is applied to every response."""

from __future__ import annotations

from httpx import AsyncClient


async def test_hardening_headers_present(client: AsyncClient) -> None:
    headers = (await client.get("/health/live")).headers
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "default-src 'none'" in headers["content-security-policy"]
    assert headers["strict-transport-security"].startswith("max-age=")
    assert "geolocation=()" in headers["permissions-policy"]


async def test_server_identity_is_stripped(client: AsyncClient) -> None:
    """No response discloses the server or a powered-by header."""
    headers = (await client.get("/v1/health")).headers
    assert "server" not in headers
    assert "x-powered-by" not in headers
