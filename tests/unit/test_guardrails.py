"""Guardrail screens: the crisis path fails closed, benign input is allowed."""

from __future__ import annotations

import pytest
from app.services.rag.guardrails import (
    CRISIS_SIGNPOST,
    BlockReason,
    GuardrailVerdict,
    check_input,
    check_output,
)


async def test_benign_input_is_allowed() -> None:
    result = await check_input("What are the Sunday service times?", locale="en")
    assert result.verdict is GuardrailVerdict.ALLOW
    assert not result.blocked


@pytest.mark.parametrize(
    "text",
    ["I want to kill myself", "thinking about suicide", "savižudybė", "убить себя"],
)
async def test_crisis_input_is_blocked_and_signed_off(text: str) -> None:
    """A crisis mention is never answered by the model; it routes to a human."""
    result = await check_input(text, locale="lt")
    assert result.blocked
    assert BlockReason.PASTORAL_CRISIS in result.reasons
    assert result.note == CRISIS_SIGNPOST


async def test_crisis_output_is_blocked_before_approval() -> None:
    result = await check_output("You should end my life soon.", locale="en")
    assert result.blocked
