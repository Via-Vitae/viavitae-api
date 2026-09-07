# Architecture — `viavitae-api`

FastAPI application exposing versioned REST endpoints under `/v1`, with service adapters for Bitrix24, Stripe and Paysera, a RAG pipeline for the pastoral assistant, and background workers for demo resets and follow-up sequences.

## Context map

```text
        clients / visitors
                │
        viavitae-web  ──►  viavitae-api  ──►  Bitrix24 · Stripe · Paysera
                │                 │
        viavitae-demos      viavitae-infra (Proxmox → k3s → Argo CD)
                │                 │
        viavitae-clients    monitoring · backup · DR
```

Shared foundations: `viavitae-brand` (tokens and guidelines), `viavitae-docs`
(compliance, runbooks, ADR index), `viavitae-qa` (cross-repository tests).

## Conventions

Routers are thin; services own behaviour; models are tenant-scoped.

## Architectural decision records

New decisions are appended here with a sequential number and are indexed in
`viavitae-docs/docs/adr/README.md`. ADR numbers are chronological identifiers,
not priority ranks.

### ADR-001 — Repository scaffold generated from the organisation blueprint

- **Status:** accepted
- **Context:** Every ViaVitae repository must carry the same compliance surface
  (README, LICENSE, SECURITY, QODER, CONTRIBUTING, CHANGELOG, `.github/`,
  `docs/architecture.md`, `docs/DPIA-template.md`).
- **Decision:** Generate the baseline from `viavitae-template`; deviations are
  recorded as ADRs in this file.
- **Consequences:** Uniform automation across the org; new repositories start
  compliant instead of becoming compliant later.

### ADR-002 — Service boundaries: one deployable, modular internals

- **Status:** accepted
- **Context:** The product surface (assessment, quotes, donations, AI, GIS,
  notifications) is broad, but the team is small and traffic is modest.
- **Decision:** Ship one FastAPI deployable with strict internal module
  boundaries (`api/v1`, `services/*`, `models`, `workers`). A module may be
  extracted into its own service only when it needs an independent scaling or
  release cadence — recorded in a new ADR.
- **Consequences:** Simple operations and one migration path; requires discipline
  to keep boundaries clean (enforced by import-linter contracts in CI).

### ADR-003 — EU data residency as an architectural constraint

- **Status:** accepted
- **Context:** Clients are Lithuanian and broader EU dioceses and parishes;
  personal data (donors, cemetery records, pastoral notes) is in scope of GDPR.
- **Decision:** All processing and storage stays in the EEA on
  self-hosted infrastructure (`viavitae-infra`). Third-party SaaS is allowed only
  with an ADR, a DPA and a documented transfer mechanism.
- **Consequences:** Stripe/Paysera and Bitrix24 integrations must be configured
  for EU regions; US-only services are rejected by default.

### ADR-004 — Tenant isolation strategy

- **Status:** accepted
- **Context:** Each parish/diocese is a tenant; data must never leak across
  tenants, and a client may request deletion of everything.
- **Decision:** Shared PostgreSQL with a `tenant_id` column on every table,
  enforced by a session-level `SET app.tenant_id` plus row-level security
  policies. Repository helpers reject queries without a tenant context.
- **Consequences:** Cheap provisioning, strong isolation, one backup/restore
  path. Requires care in migrations (RLS policies are part of every migration).

### ADR-005 — Idempotency for money-moving and webhook endpoints

- **Status:** accepted
- **Context:** Stripe, Paysera and Bitrix24 all retry webhooks; a duplicate
  donation must not create a duplicate receipt or a duplicate CRM contact.
- **Decision:** Every mutating endpoint that moves money or is called by an
  external system requires an idempotency key (`Idempotency-Key` header or the
  provider event id). Keys are stored with the request hash and result for 30
  days; replays return the stored result with `200` and `Idempotent-Replayed: true`.
- **Consequences:** Safe retries, exactly-once side effects. Adds a table and a
  dependency; keys must be validated for reuse with a different payload (`409`).

### ADR-006 — Error envelope and versioning

- **Status:** accepted
- **Context:** Multiple clients (web, demos, client tenants, marketplace) consume
  the API and need stable, machine-readable errors.
- **Decision:** One envelope `{"error": {"code", "message", "details",
  "request_id"}}` with documented `code` values per endpoint; version prefix `/v1`
  in the path; additive changes only within a version; removals follow
  expand-contract with a deprecation header for at least 6 months.
- **Consequences:** Clients can branch on codes rather than strings; the OpenAPI
  document in `docs/api/v1-openapi.json` is generated from the app and diffed in CI.

### ADR-007 — AI pastoral assistant: retrieval-grounded with human approval

- **Status:** accepted
- **Context:** Clergy want drafting help; publishing unreviewed AI text in a
  religious context is unacceptable reputationally and pastorally.
- **Decision:** RAG over the tenant's own approved corpus only, with mandatory
  citations, guardrails (`services/rag/guardrails.py`) for doctrine/safety, and
  **no** automatic publication: every draft enters `services/approvals.py` and
  requires a named human approver. Model provider must be EU-resident or run
  self-hosted; prompts and outputs are logged without personal data.
- **Consequences:** Higher latency to publication, full auditability. DPIA-002
  applies; re-review on any model or provider change.

## Cross-cutting concerns

| Concern | Approach |
| --- | --- |
| Security headers | Enforced at the edge and re-checked in CI |
| Secret management | Environment-scoped secrets, never in git; Gitleaks gate |
| Observability | Structured JSON logs → Loki, metrics → Prometheus, dashboards in Grafana |
| Backups | Nightly with `wal-g`, restore drills documented in `viavitae-docs` |
| Accessibility | WCAG 2.2 AA, `axe` in CI, keyboard-first components |
| i18n | `lt`, `en`, `ru` supported; `pl`, `de` stubbed |
