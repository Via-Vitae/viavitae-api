"""Bitrix24 client contract: request shape and error translation, no network."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
from app.services.bitrix24.client import Bitrix24Client, Bitrix24Error

WEBHOOK = "https://crm.example.eu/rest/1/secret/"
FIXTURE = Path(__file__).parent / "fixtures" / "lead_add.json"


async def test_add_lead_posts_expected_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """Lead creation always carries SOURCE_ID so attribution is stable."""
    client = Bitrix24Client(webhook_url=WEBHOOK)
    recorded = json.loads(FIXTURE.read_text())
    captured: dict[str, object] = {}

    async def fake_call(method: str, fields: dict[str, object]) -> object:
        captured["method"] = method
        captured["fields"] = fields
        return recorded["result"]

    monkeypatch.setattr(client, "call", fake_call)
    lead_id = await client.add_lead({"TITLE": "Parish of St Anne"})
    assert lead_id == 42
    assert captured["method"] == "crm.lead.add"
    assert captured["fields"] == {
        "fields": {"TITLE": "Parish of St Anne", "SOURCE_ID": "VIATAVAITAE_API"}
    }


async def test_error_response_is_translated(monkeypatch: pytest.MonkeyPatch) -> None:
    """A provider error becomes a Bitrix24Error carrying the HTTP status."""
    client = Bitrix24Client(webhook_url=WEBHOOK)

    async def fake_post(self: httpx.AsyncClient, url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(404, content=json.dumps({"error": "NOT_FOUND"}).encode())

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    with pytest.raises(Bitrix24Error) as excinfo:
        await client.call("crm.lead.get", {"id": 1})
    assert excinfo.value.status_code == 404


def test_client_requires_a_configured_webhook() -> None:
    """Without a webhook URL the client refuses to construct (fail fast)."""
    with pytest.raises(Bitrix24Error):
        Bitrix24Client(webhook_url=None)
