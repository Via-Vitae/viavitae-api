"""AI pastoral assistant DTOs (retrieval-grounded, human-approved; DPIA-002)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

DRAFT_STATE_PATTERN = r"^(pending|approved|rejected|withdrawn|expired)$"


class Citation(BaseModel):
    """A retrieved source that grounds part of a draft."""

    model_config = ConfigDict(frozen=True)

    source_id: str
    document_title: str
    excerpt: str


class DraftCreate(BaseModel):
    """A request to queue a retrieval-grounded draft."""

    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=1, max_length=4000)
    locale: str = Field(default="lt", pattern=r"^(lt|en|ru)$")


class Draft(BaseModel):
    """A draft with its citations and grounding coverage."""

    model_config = ConfigDict(frozen=True)

    draft_id: str
    state: str = Field(pattern=DRAFT_STATE_PATTERN)
    text: str
    citations: list[Citation]
    coverage_ratio: float = Field(ge=0.0, le=1.0)


class DraftDecision(BaseModel):
    """An approve/reject decision by a named human approver."""

    model_config = ConfigDict(extra="forbid")

    approve: bool
    reason: str = Field(default="", max_length=1000)


class AuditEntry(BaseModel):
    """One append-only entry in the approval audit trail."""

    model_config = ConfigDict(frozen=True)

    draft_id: str
    decided_by: str
    decision: str
    decided_at: str
