"""GIS endpoints: consent-gated and idempotent; scaffold -> 501."""

from __future__ import annotations

from httpx import AsyncClient


async def test_parcels_is_scaffolded(client: AsyncClient) -> None:
    assert (await client.get("/v1/gis/parcels")).status_code == 501


async def test_reservation_requires_a_strong_idempotency_key(client: AsyncClient) -> None:
    """A too-short key fails validation before any side effect (ADR-005)."""
    bad = await client.post(
        "/v1/gis/reservations", json={"parcel_id": "p1", "idempotency_key": "short"}
    )
    assert bad.status_code == 422
    ok = await client.post(
        "/v1/gis/reservations",
        json={"parcel_id": "p1", "idempotency_key": "0123456789abcdef"},
    )
    assert ok.status_code == 501
