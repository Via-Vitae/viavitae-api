"""Retrieval over the tenant's approved corpus and citation assembly (DPIA-002).

Two responsibilities kept together because they share the retrieval contract:
``retrieve`` finds the approved chunks for a tenant/locale, and ``audit`` checks
that a generated draft is grounded in those chunks before it may enter the
approval queue.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass(slots=True, frozen=True)
class Chunk:
    """One indexed piece of a tenant document."""

    source_id: str
    document_title: str
    text: str
    score: float
    locale: str


@dataclass(slots=True, frozen=True)
class RetrievalResult:
    """Retrieved chunks with the query actually used."""

    query: str
    chunks: tuple[Chunk, ...]

    @property
    def empty(self) -> bool:
        """True when nothing relevant was found - the draft must say so."""
        return not self.chunks


async def retrieve(
    *, tenant_id: str, query: str, locale: str, top_k: int | None = None
) -> RetrievalResult:
    """Retrieve the most relevant approved chunks for a tenant and locale.

    Hard rules (ADR-007):
      * scope is **always** the requesting tenant - cross-tenant retrieval is a
        security incident, not a bug;
      * only documents in `approved` state are indexed;
      * no personal data enters the index (documents are screened at ingest);
      * `top_k` is capped by settings to keep prompts and cost predictable.
    """
    limit = min(top_k or settings.rag_top_k, 20)
    # TODO(api): embed `query`, run a hybrid (vector + keyword) search with a
    #            tenant filter and RLS, re-rank, and return Chunk objects.
    _ = (tenant_id, locale, limit)
    return RetrievalResult(query=query, chunks=())


@dataclass(slots=True, frozen=True)
class Citation:
    """A claim in the draft tied to a retrieved source."""

    source_id: str
    document_title: str
    excerpt: str
    span_start: int
    span_end: int


@dataclass(slots=True, frozen=True)
class CitationAudit:
    """Result of verifying a draft against its retrieved sources."""

    citations: tuple[Citation, ...]
    unsupported_claims: tuple[str, ...]
    coverage_ratio: float

    @property
    def publishable(self) -> bool:
        """A draft with unsupported claims never leaves the approval queue."""
        return not self.unsupported_claims


def audit(draft: str, citations: list[Citation]) -> CitationAudit:
    """Check that sentences in `draft` are grounded in `citations`.

    Ungrounded sentences are reported, not silently dropped: the human approver
    must see exactly what the model invented.
    """
    unsupported: list[str] = []
    cited = len(citations)
    sentences = [part.strip() for part in draft.replace("?", ".!").split(".") if part.strip()]
    total = len(sentences) or 1
    # TODO(api): match each sentence against citation excerpts (embedding or
    #            lexical overlap) and collect the unmatched ones into `unsupported`.
    coverage = min(1.0, cited / total)
    return CitationAudit(
        citations=tuple(citations),
        unsupported_claims=tuple(unsupported),
        coverage_ratio=coverage,
    )
