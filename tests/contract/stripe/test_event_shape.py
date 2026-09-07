"""Stripe event fixtures pin the shape the webhook handler must accept."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "checkout_completed.json"


@pytest.mark.contract
def test_recorded_event_has_the_expected_envelope() -> None:
    event = json.loads(FIXTURE.read_text())
    assert event["id"].startswith("evt_")
    assert event["type"] == "checkout.session.completed"
    session = event["data"]["object"]
    assert session["currency"] == "eur"
    assert isinstance(session["amount_total"], int)  # amounts are integer minor units


@pytest.mark.contract
def test_signature_verification_contract() -> None:
    pytest.skip("TODO(api): verify stripe.Webhook.construct_event against a signed payload")
