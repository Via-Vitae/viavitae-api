"""Stripe webhook: fail-closed on a missing signature or unconfigured secret."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

EVENT = b'{"id": "evt_test_1", "type": "checkout.session.completed"}'


async def test_missing_signature_is_rejected(client: AsyncClient) -> None:
    """No signature header -> 400; nothing is acknowledged or processed."""
    response = await client.post(
        "/v1/webhooks/stripe", content=EVENT, headers={"content-type": "application/json"}
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "missing_signature"


async def test_signed_event_is_not_acked_without_a_configured_secret(client: AsyncClient) -> None:
    """A signature alone is not enough: with no secret the event is not accepted."""
    response = await client.post(
        "/v1/webhooks/stripe",
        content=EVENT,
        headers={"content-type": "application/json", "stripe-signature": "t=1,v1=abc"},
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "webhook_not_configured"


async def test_health_reports_unconfigured(client: AsyncClient) -> None:
    assert (await client.get("/v1/webhooks/stripe/health")).status_code == 503


@pytest.mark.contract
async def test_replayed_event_is_idempotent(client: AsyncClient) -> None:
    """Replaying one event id yields a single side effect and 200 both times."""
    pytest.skip("TODO(api): assert idempotent replay once signature verification lands")
