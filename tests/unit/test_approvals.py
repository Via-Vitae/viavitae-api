"""Approval workflow invariants: nothing is publishable without an approval."""

from __future__ import annotations

import pytest
from app.services.approvals import (
    ApprovalRequiredError,
    ApprovalService,
    ApprovalState,
    ContentType,
)


async def test_assert_publishable_without_approval_raises() -> None:
    """No approval record for the content hash means it cannot be published."""
    service = ApprovalService()
    with pytest.raises(ApprovalRequiredError):
        await service.assert_publishable(draft_id="d1", content_hash="abc123")


async def test_submit_and_decide_are_scaffolded() -> None:
    """Persistence of the queue/decision is not implemented yet (fail closed)."""
    service = ApprovalService()
    with pytest.raises(NotImplementedError):
        await service.submit(
            draft_id="d1",
            tenant_id="anne",
            content_type=ContentType.PASTORAL_TEXT,
            content_hash="abc",
            author="author@viavitae.eu",
        )
    with pytest.raises(NotImplementedError):
        await service.decide(
            draft_id="d1",
            approver="approver@viavitae.eu",
            approve=True,
            reason="ok",
            content_hash="abc",
        )


def test_states_and_content_types_are_stable_strings() -> None:
    assert ApprovalState.APPROVED == "approved"
    assert ApprovalState.PENDING == "pending"
    assert ContentType.PASTORAL_TEXT == "pastoral_text"
