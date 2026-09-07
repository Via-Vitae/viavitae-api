"""Bitrix24 building blocks: field mapping, circuit breaker and batch sync."""

from __future__ import annotations

import pytest
from app.services.bitrix24 import mapper
from app.services.bitrix24.circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
)
from app.services.bitrix24.sync import BatchSync


def test_assessment_to_lead_maps_fields_and_keeps_utm() -> None:
    lead = mapper.assessment_to_lead(
        {"title": "St Anne", "email": "a@b.c", "utm_source": "google", "utm_medium": ""}
    )
    assert lead["TITLE"] == "St Anne"
    assert lead["EMAIL"] == "a@b.c"
    assert lead["UF_CRM_VV_UTM_SOURCE"] == "google"
    assert "UF_CRM_VV_UTM_MEDIUM" not in lead  # empty UTM values are dropped


def test_lead_to_domain_is_the_inverse_and_ignores_unknown_fields() -> None:
    domain = mapper.lead_to_domain({"TITLE": "St Anne", "EMAIL": "a@b.c", "OTHER": 1})
    assert domain == {"title": "St Anne", "email": "a@b.c"}


async def test_breaker_opens_after_the_failure_threshold() -> None:
    breaker = CircuitBreaker(name="t", failure_threshold=2, recovery_seconds=100)
    for _ in range(2):
        with pytest.raises(RuntimeError):
            async with breaker:
                raise RuntimeError("boom")
    assert breaker.state is CircuitState.OPEN
    with pytest.raises(CircuitOpenError):
        async with breaker:
            pass


async def test_breaker_half_opens_then_closes_on_a_successful_probe() -> None:
    breaker = CircuitBreaker(name="t", failure_threshold=1, recovery_seconds=0, success_threshold=1)
    with pytest.raises(RuntimeError):
        async with breaker:
            raise RuntimeError("boom")
    assert breaker.state is CircuitState.OPEN
    async with breaker:  # recovery window elapsed -> half-open probe succeeds
        pass
    assert breaker.state is CircuitState.CLOSED


class _OkClient:
    async def call(self, method: str, fields: dict[str, object]) -> object:
        return {"result": "ok"}


class _BadClient:
    async def call(self, method: str, fields: dict[str, object]) -> object:
        raise RuntimeError("crm down")


async def test_batch_sync_counts_successes() -> None:
    result = await BatchSync(_OkClient()).run("crm.lead.add", [{"TITLE": "a"}, {"TITLE": "b"}])  # type: ignore[arg-type]
    assert result.succeeded == 2
    assert result.ok is True


async def test_batch_sync_isolates_failures() -> None:
    result = await BatchSync(_BadClient()).run("crm.lead.add", [{"TITLE": "a"}])  # type: ignore[arg-type]
    assert result.succeeded == 0
    assert result.ok is False
    assert len(result.failed) == 1
