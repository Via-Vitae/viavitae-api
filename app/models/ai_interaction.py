"""AI queries, generated answers, citations and approval decisions (DPIA-002)."""

from __future__ import annotations

# TODO(api): define the ORM models for `ai_interaction` using Base, IdMixin,
# TimestampMixin and TenantScopedMixin from app.models.base.
#
# Tables:
#   * ai_query(tenant_id, locale, prompt_hash, guardrail_verdict, created_at)
#     - prompt text is not stored verbatim when it may carry personal data;
#   * ai_answer(query_id, draft_text, content_hash, state, model_ref);
#   * ai_citation(answer_id, source_id, document_title, excerpt, span);
#   * ai_approval(answer_id, decided_by, decision, reason, decided_at) -
#     append-only, author != approver enforced in app/services/approvals.py.
#
# Rules:
#   * nothing is published without an APPROVED record for the exact content hash;
#   * timestamps are timezone-aware UTC; no column stores a secret;
#   * every table is tenant-scoped and gets an RLS policy in the migration.
