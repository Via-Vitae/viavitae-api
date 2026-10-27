"""Stripe webhook: fail-closed guards, and the stub never acknowledges events.

Current implementation status (ADR-005): signature verification and the
idempotency ledger are NOT implemented; every guarded request is refused with
501 before any processing. The replay test below therefore pins the truthful
contract for today — a replayed event is never acknowledged or applied — and
must be superseded, not deleted, when real processing lands.
"""

from __future__ import annotations

import pytest
from app.core.config import settings
from fastapi import status
from httpx import AsyncClient
from pydantic import SecretStr

EVENT = b'{"id": "evt_test_1", "type": "checkout.session.completed"}'

# One signed-but-unprocessed replay pair per provider, at the mounted stub path.
# Every case carries a syntactically present (not cryptographically valid)
# signature: the stub must refuse it on the processing branch, never accept it.
_STUB_REPLAY_CASES = [
    pytest.param(
        "/v1/webhooks/stripe",
        {
            "content": EVENT,
            "headers": {
                "content-type": "application/json",
                "stripe-signature": "t=1,v1=abc",
            },
        },
        id="stripe",
    ),
    pytest.param(
        "/v1/webhooks/paysera?ss2=deadbeef",
        {"content": b"order_id=1"},
        id="paysera",
    ),
    pytest.param(
        "/v1/webhooks/bitrix24",
        {
            "content": EVENT,
            "headers": {
                "content-type": "application/json",
                "x-bitrix-token": "tok",
            },
        },
        id="bitrix24",
    ),
]


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


@pytest.fixture
def providers_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set every provider secret so requests reach the processing branch.

    Without this the handlers stop at the 503 "secret not configured" guard and
    the assertions below would only re-test that guard — a pin that cannot see
    the code it is meant to protect.
    """
    monkeypatch.setattr(settings, "stripe_webhook_secret", SecretStr("whsec_test"))
    monkeypatch.setattr(settings, "paysera_sign_password", SecretStr("sign_test"))
    monkeypatch.setattr(settings, "bitrix24_webhook_url", SecretStr("https://bx.invalid/hook"))


@pytest.mark.parametrize(("path", "send_kwargs"), _STUB_REPLAY_CASES)
async def test_replayed_event_is_never_acked_or_applied(
    providers_configured: None, client: AsyncClient, path: str, send_kwargs: dict[str, object]
) -> None:
    """Pins the fail-closed stub contract: replaying the same signed event
    twice must produce two identical NON-2xx responses — no acknowledgment on
    either attempt — so the provider keeps retrying and no payment or CRM side
    effect is ever applied (or double-applied) by this endpoint.

    The providers are configured here so the request actually reaches the
    processing branch. When signature verification, the webhook_event ledger and
    processing land together, replace this pin with the positive 200-once ledger
    assertion — never relax it in place.
    """
    first = await client.post(path, **send_kwargs)
    second = await client.post(path, **send_kwargs)

    assert not first.is_success, f"{path}: stub acknowledged an event ({first.status_code})"
    assert not second.is_success, f"{path}: replay was acknowledged ({second.status_code})"
    # Reaching this branch proves the guards passed; the stub must still refuse.
    assert first.status_code == status.HTTP_501_NOT_IMPLEMENTED, (
        f"{path}: expected the 501 not_implemented stub, got {first.status_code}"
    )
    assert first.json()["error"]["code"] == "not_implemented"
    assert second.status_code == first.status_code
    assert second.json()["error"]["code"] == first.json()["error"]["code"]
    assert "idempotent-replayed" not in {k.lower() for k in second.headers}, (
        "the runbook's replay header must not appear while no idempotency "
        "ledger exists (docs/runbooks/webhook-replay.md)"
    )


_SIGNED_EVENT_HEADERS = {
    "content-type": "application/json",
    "stripe-signature": "t=1,v1=abc",
}


@pytest.mark.contract
@pytest.mark.xfail(
    strict=True,
    reason=(
        "ADR-005 is not implemented: no signature verification and no webhook_event "
        "ledger, so a replay cannot be served from a stored result. Expected to fail "
        "today; it becomes a hard XPASS failure the moment processing lands, which is "
        "the signal to replace test_replayed_event_is_never_acked_or_applied."
    ),
)
async def test_replayed_event_is_idempotent(
    providers_configured: None, client: AsyncClient
) -> None:
    """DESIGN acceptance test (ADR-005): one event id yields one side effect and
    ``200`` on both deliveries, the second served from the ledger.

    A skip would be invisible: it never announces when the implementation
    arrives. ``xfail(strict=True)`` keeps the contract executable and self-flags.
    """
    first = await client.post("/v1/webhooks/stripe", content=EVENT, headers=_SIGNED_EVENT_HEADERS)
    second = await client.post("/v1/webhooks/stripe", content=EVENT, headers=_SIGNED_EVENT_HEADERS)
    assert first.status_code == status.HTTP_200_OK
    assert second.status_code == status.HTTP_200_OK
    assert second.headers.get("idempotent-replayed") == "true"
