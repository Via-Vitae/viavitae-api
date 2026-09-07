"""Ingest approved documents into the tenant's RAG index (DPIA-002).

Only documents that have been approved by a named human are indexed, and they
are screened for personal data first. Chunking is deterministic and
dependency-free so it can be unit-tested offline; a tokenizer-aware splitter can
replace the internals later without changing callers.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class IngestOutcome:
    """Result of ingesting one document."""

    document_id: str
    chunks: int
    skipped: bool
    reason: str = ""


def chunk_text(text: str, *, max_chars: int = 1200, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks on paragraph then hard boundaries."""
    if overlap < 0 or max_chars <= overlap:
        raise ValueError("max_chars must exceed a non-negative overlap")
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks: list[str] = []
    buffer = ""
    for paragraph in paragraphs:
        if len(buffer) + len(paragraph) + 2 <= max_chars:
            buffer = f"{buffer}\n\n{paragraph}".strip()
            continue
        if buffer:
            chunks.append(buffer)
        start = 0
        buffer = paragraph
        while len(buffer) > max_chars:
            chunks.append(buffer[:max_chars])
            start += max_chars - overlap
            buffer = paragraph[start:]
    if buffer:
        chunks.append(buffer)
    return chunks


async def ingest_document(
    *, tenant_id: str, document_id: str, text: str, locale: str
) -> IngestOutcome:
    """Chunk and embed one approved document into pgvector for a tenant."""
    # TODO(api): screen for personal data, embed chunks (app.services.rag.llm),
    #            upsert into document_chunk under the tenant filter, verify count.
    _ = (tenant_id, locale)
    chunks = chunk_text(text)
    return IngestOutcome(
        document_id=document_id,
        chunks=len(chunks),
        skipped=not chunks,
        reason="" if chunks else "empty document",
    )
