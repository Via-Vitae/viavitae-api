"""Assessment funnel endpoint contract (validation -> 422, scaffold -> 501)."""

from __future__ import annotations

from httpx import AsyncClient

VALID = {"parish": "Parish of St Anne", "congregation_size": 500, "locale": "lt"}


async def test_submit_rejects_an_invalid_body(client: AsyncClient) -> None:
    """An empty parish (and a missing size) fails validation before any work."""
    response = await client.post("/v1/assessment/", json={"parish": ""})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


async def test_submit_valid_body_is_scaffolded(client: AsyncClient) -> None:
    """A valid submission reaches the handler, which is not implemented yet."""
    response = await client.post("/v1/assessment/", json=VALID)
    assert response.status_code == 501
    assert response.json()["error"]["code"] == "not_implemented"


async def test_get_assessment_is_scaffolded(client: AsyncClient) -> None:
    response = await client.get("/v1/assessment/11111111-1111-4111-8111-111111111111")
    assert response.status_code == 501
