# QODER.md — agent operating manual for `viavitae-api`

Rules for AI coding agents (Qoder and equivalents) working in this repository.
They complement, and never override, `CONTRIBUTING.md` and `SECURITY.md`.

## 1. What this repository is

Backend services (Python 3.12 + FastAPI): assessment funnel, pricing engine and PDF quotes, idempotent payment/CRM webhooks, donations and impact aggregation, the RAG-based AI pastoral assistant with a human approval queue, cemetery GIS, and notification dispatch. PostgreSQL, tenant-scoped, EU-resident.

## 2. Commands

```bash
uv sync                       # or: pip install -e ".[dev]"
uv run ruff check --fix .     # lint
uv run mypy app               # strict type check
uv run pytest                 # unit + contract tests
uv run alembic upgrade head   # migrations
uv run uvicorn app.main:app --reload --port 8000
k6 run deployments/k6/smoke.js   # smoke load
```

## 3. Conventions

- Ruff (lint + format) and mypy `strict = true`; no untyped definitions.
- Layering: `api/v1` (HTTP contracts) → `services` (business logic) → `models`
  (persistence). Routers contain no business logic.
- Pydantic v2 schemas for every request/response; the OpenAPI document is the
  contract published in `docs/api/v1-openapi.json`.
- Error envelope: `{"error": {"code", "message", "details", "request_id"}}` —
  never leak stack traces or internals to clients.
- Every query is tenant-scoped; the tenant comes from the authenticated context,
  never from a request body field.
- Migrations are expand-contract and always reversible.
- Idempotency keys required on all money-moving and webhook endpoints.
- Structured JSON logs with `request_id`; no personal data in logs.

## 4. Guardrails — do not do these

- **Never** log personal data, tokens, card numbers or pastoral content.
- **Never** write to the database from a router — go through a service.
- **Never** add an outbound integration outside the EEA without an ADR + DPA.
- **Never** publish AI-generated pastoral content without an approval record;
  `services/approvals.py` is the only path to publication.
- **Never** squash or edit an applied migration; add a new one.
- **Never** skip webhook signature verification (Stripe, Paysera, Bitrix24).
- **Never** widen a permission scope to make a test pass.

## 5. Definition of done for an agent task

1. The change compiles/type-checks and the relevant test subset passes.
2. `CHANGELOG.md` has an entry under `[Unreleased]`.
3. Documentation touched whenever behaviour, contracts or configuration changed.
4. No new dependency without checking licence (EU-OK, OSI-approved) and
   maintenance status; record the decision in the pull request.
5. No secrets, no personal data, no production endpoints in code or tests.
6. The diff is the smallest reversible change that satisfies the request.

## 6. Where to look next

| Need | Location |
| --- | --- |
| Organisation-wide policy | `.github` repository |
| Design tokens & brand rules | `viavitae-brand` |
| Architecture decisions | `docs/architecture.md` and `viavitae-docs/docs/adr/` |
| GDPR records & DPIA template | `docs/DPIA-template.md`, `viavitae-docs/docs/gdpr/` |
| Runbooks | `viavitae-docs/docs/runbooks/` |
| Shared tests & fixtures | `viavitae-qa` |
