"""Donation endpoints: money is a typed object; scaffold -> 501."""

from __future__ import annotations

from httpx import AsyncClient


async def test_impact_is_scaffolded(client: AsyncClient) -> None:
    assert (await client.get("/v1/donations/impact")).status_code == 501


async def test_history_is_scaffolded(client: AsyncClient) -> None:
    assert (await client.get("/v1/donations/history")).status_code == 501


async def test_create_requires_a_money_object(client: AsyncClient) -> None:
    """A non-integer amount is rejected; a valid Money object reaches the handler."""
    bad = await client.post("/v1/donations/", json={"amount": {"amount_minor": "free"}})
    assert bad.status_code == 422
    ok = await client.post("/v1/donations/", json={"amount": {"amount_minor": 1000}})
    assert ok.status_code == 501
