"""AI pastoral endpoints: drafting is scaffolded and approval-gated (ADR-007)."""

from __future__ import annotations

from httpx import AsyncClient


async def test_create_draft_is_scaffolded(
    client: AsyncClient, tenant_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/v1/ai/drafts",
        json={"prompt": "A short homily on hope.", "locale": "lt"},
        headers=tenant_headers,
    )
    assert response.status_code == 501


async def test_audit_trail_is_scaffolded(
    client: AsyncClient, tenant_headers: dict[str, str]
) -> None:
    assert (await client.get("/v1/ai/audit", headers=tenant_headers)).status_code == 501


async def test_decision_requires_the_approve_flag(
    client: AsyncClient, tenant_headers: dict[str, str]
) -> None:
    """The decision body must carry an explicit approve/reject."""
    response = await client.post("/v1/ai/drafts/d1/decision", json={}, headers=tenant_headers)
    assert response.status_code == 422
