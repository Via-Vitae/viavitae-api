"""Cemetery sections, parcels, geometry and reservations."""

from __future__ import annotations

# TODO(api): define the ORM models for `gis` using Base, IdMixin,
# TimestampMixin and TenantScopedMixin from app.models.base.
#
# Rules:
#   * every table is tenant-scoped and gets an RLS policy in the migration;
#   * money is stored as integer minor units plus a currency code;
#   * timestamps are timezone-aware UTC;
#   * no column stores a secret;
#   * personal data columns are annotated with their retention rule.
