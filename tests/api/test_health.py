"""Health, readiness and version probes -- the smallest end-to-end assertion."""

from __future__ import annotations

from httpx import AsyncClient


async def test_liveness_is_always_ok(client: AsyncClient) -> None:
    """Liveness must not depend on any external system."""
    response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_request_id_is_returned(client: AsyncClient) -> None:
    """Every response carries a request id for correlation."""
    response = await client.get("/health/live")
    assert response.headers.get("x-request-id")


async def test_v1_health_is_ok(client: AsyncClient) -> None:
    response = await client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_v1_version_exposes_non_sensitive_metadata(client: AsyncClient) -> None:
    body = (await client.get("/v1/version")).json()
    assert body["service"] == "viavitae-api"
    assert body["version"]
    assert body["environment"]
