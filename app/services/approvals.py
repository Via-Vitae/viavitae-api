"""Content-approval workflow engine — the only path to publication."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any


class ApprovalState(StrEnum):
    """Lifecycle of a draft awaiting publication."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class ContentType(StrEnum):
    """What can be submitted for approval."""

    PASTORAL_TEXT = "pastoral_text"
    ANNOUNCEMENT = "announcement"
    OBITUARY = "obituary"
    HOMILY_DRAFT = "homily_draft"
    PRODUCT_DESCRIPTION = "product_description"


@dataclass(slots=True, frozen=True)
class ApprovalRecord:
    """Immutable audit entry for one decision."""

    draft_id: str
    tenant_id: str
    content_type: ContentType
    state: ApprovalState
    decided_by: str | None
    decided_at: datetime | None
    reason: str
    content_hash: str
    citations: tuple[Any, ...] = ()


class ApprovalRequiredError(RuntimeError):
    """Raised when a caller tries to publish without an approval record."""


class ApprovalService:
    """Queue, decide and audit content approvals.

    Invariants (ADR-007):
      * nothing is published without an `APPROVED` record for the exact content
        hash that was reviewed — editing after approval resets the state;
      * the approver is a named human identity, never a service account;
      * self-approval is rejected: author and approver must differ;
      * decisions are append-only and retained for the audit period.
    """

    async def submit(
        self,
        *,
        draft_id: str,
        tenant_id: str,
        content_type: ContentType,
        content_hash: str,
        author: str,
        citations: tuple[Any, ...] = (),
    ) -> ApprovalRecord:
        """Add a draft to the approval queue."""
        # TODO(api): persist the queue entry and notify the configured approvers.
        _ = (draft_id, tenant_id, content_type, content_hash, author, citations)
        raise NotImplementedError("approval submission is scaffolded but not implemented")

    async def decide(
        self, *, draft_id: str, approver: str, approve: bool, reason: str, content_hash: str
    ) -> ApprovalRecord:
        """Record an approval or rejection decision."""
        # TODO(api): enforce author != approver, verify content_hash, append the
        #            audit record, and publish only when approved.
        _ = (draft_id, approver, approve, reason, content_hash)
        raise NotImplementedError("approval decision is scaffolded but not implemented")

    async def assert_publishable(self, *, draft_id: str, content_hash: str) -> ApprovalRecord:
        """Raise unless an approval exists for this exact content hash."""
        # TODO(api): load the latest record and validate state + hash.
        _ = (draft_id, content_hash)
        raise ApprovalRequiredError(f"draft {draft_id} has no approval for hash {content_hash}")
