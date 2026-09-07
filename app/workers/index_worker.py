"""RAG re-index worker: re-embeds a tenant document after an update.

Triggered when an approved document changes so the vector index never serves a
stale answer. Re-indexing is idempotent at the document level: the worker
replaces the document's chunks rather than appending.
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.services.rag.ingest import IngestOutcome, ingest_document

logger = get_logger(__name__)


async def reindex(*, tenant_id: str, document_id: str, text: str, locale: str) -> IngestOutcome:
    """Re-chunk and re-embed one approved document for a tenant."""
    logger.info("index.reindex_started", tenant_id=tenant_id, document_id=document_id)
    outcome = await ingest_document(
        tenant_id=tenant_id, document_id=document_id, text=text, locale=locale
    )
    logger.info("index.reindex_done", document_id=document_id, chunks=outcome.chunks)
    return outcome
