"""RAG drafting with a mandatory human approval queue (DPIA-002, ADR-007).

The route shape is draft-centric (create draft -> fetch with citations ->
record a decision -> audit trail) because it makes the "nothing is published
without a named human approval" invariant explicit in the API surface.
"""

from __future__ import annotations

from fastapi import APIRouter, status

from app.schemas.ai import AuditEntry, Draft, DraftCreate, DraftDecision

router = APIRouter(tags=["ai_pastoral"])


@router.post(
    "/drafts",
    response_model=Draft,
    status_code=status.HTTP_201_CREATED,
    summary="Queue a retrieval-grounded draft.",
)
async def create_draft(body: DraftCreate) -> Draft:
    """Retrieve over the tenant's approved corpus and queue a cited draft.

    TODO(api): run guardrails.check_input, retrieve, generate via rag.llm, audit
    citations (rag.retrieve.audit), then enqueue for approval. Nothing is
    published here (ADR-007).
    """
    raise NotImplementedError("create_draft is scaffolded but not implemented")


@router.get("/drafts/{draft_id}", response_model=Draft, summary="Fetch a draft with its citations.")
async def get_draft(draft_id: str) -> Draft:
    """Fetch one draft and its citations for the resolved tenant."""
    raise NotImplementedError("get_draft is scaffolded but not implemented")


@router.post(
    "/drafts/{draft_id}/decision",
    response_model=Draft,
    status_code=status.HTTP_201_CREATED,
    summary="Approve or reject a draft; the decision is audited.",
)
async def decide_draft(draft_id: str, body: DraftDecision) -> Draft:
    """Record an approval/rejection by a named human (author != approver).

    TODO(api): delegate to app.services.approvals and append the audit record.
    """
    raise NotImplementedError("decide_draft is scaffolded but not implemented")


@router.get(
    "/audit", response_model=list[AuditEntry], summary="Approval audit trail for the tenant."
)
async def get_audit() -> list[AuditEntry]:
    """Return the append-only approval audit trail for the tenant."""
    raise NotImplementedError("get_audit is scaffolded but not implemented")
