"""Approved source documents, chunks and embeddings for the RAG index (DPIA-002)."""

from __future__ import annotations

# TODO(api): define the ORM models for `ai_document` using Base, IdMixin,
# TimestampMixin and TenantScopedMixin from app.models.base.
#
# Tables:
#   * document(tenant_id, title, locale, state, source_uri, content_hash,
#     approved_by, approved_at) - only `approved` documents are indexed;
#   * document_chunk(document_id, ordinal, text, embedding vector, token_count)
#     - embedding uses pgvector; screened at ingest so no personal data is stored.
#
# Rules:
#   * a document is indexed only after human approval (app/services/approvals.py);
#   * re-indexing on update is handled by app/workers/index_worker.py;
#   * timestamps are timezone-aware UTC; no column stores a secret;
#   * every table is tenant-scoped and gets an RLS policy in the migration.
