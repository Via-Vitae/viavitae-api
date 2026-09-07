"""Webhook events and the idempotency ledger (ADR-005).

Stores every verified provider event by its provider event id so a replayed
delivery is acknowledged from the stored result instead of re-running side
effects, plus client ``Idempotency-Key`` records for money-moving endpoints.
"""

from __future__ import annotations

# TODO(api): define the ORM models for `webhook_event` using Base, IdMixin,
# TimestampMixin and TenantScopedMixin from app.models.base.
#
# Tables:
#   * webhook_event(provider, provider_event_id, tenant_id, received_at,
#     payload_hash, status) with UNIQUE(provider, provider_event_id);
#   * idempotency_key(scope, key, tenant_id, request_hash, response, expires_at)
#     with UNIQUE(scope, key, tenant_id) and a 30-day expiry.
#
# Rules:
#   * a replayed key with a different request_hash is a 409 conflict;
#   * timestamps are timezone-aware UTC;
#   * no column stores a secret or raw card data;
#   * every table is tenant-scoped and gets an RLS policy in the migration.
