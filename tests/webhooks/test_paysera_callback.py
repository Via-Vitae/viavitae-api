"""Paysera callback: fail-closed without an ss2 signature or configured secret."""

from __future__ import annotations

from httpx import AsyncClient


async def test_missing_signature_is_rejected(client: AsyncClient) -> None:
    response = await client.post("/v1/webhooks/paysera", content=b"order_id=1")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "missing_signature"


async def test_signed_callback_needs_a_configured_secret(client: AsyncClient) -> None:
    response = await client.post("/v1/webhooks/paysera?ss2=deadbeef", content=b"order_id=1")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "webhook_not_configured"


async def test_health_reports_unconfigured(client: AsyncClient) -> None:
    assert (await client.get("/v1/webhooks/paysera/health")).status_code == 503
