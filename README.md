# viavitae-api

[![CI](https://github.com/Via-Vitae/viavitae-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Via-Vitae/viavitae-api/actions/workflows/ci.yml)
[![Compliance](https://github.com/Via-Vitae/viavitae-api/actions/workflows/compliance-check.yml/badge.svg)](https://github.com/Via-Vitae/viavitae-api/actions/workflows/compliance-check.yml)
[![CodeQL](https://github.com/Via-Vitae/viavitae-api/actions/workflows/codeql.yml/badge.svg)](https://github.com/Via-Vitae/viavitae-api/actions/workflows/codeql.yml)
[![Licence](https://img.shields.io/badge/licence-Proprietary-0E1B3D?labelColor=F7F4EC)](LICENSE)
[![EU hosted](https://img.shields.io/badge/hosted-EU-0E1B3D?labelColor=F7F4EC)](SECURITY.md)

> FastAPI backend for the ViaVitae platform: Bitrix24 CRM integration, Stripe and
> Paysera payment webhooks, RAG-powered pastoral AI assistant, GIS cemetery mapping,
> multi-tenant Postgres with row-level security, and a donation management API.

ViaVitae builds church-vertical websites, e-commerce and a marketplace for an EU pilot
in Lithuania, on self-hosted Proxmox infrastructure. Personal data stays in the EEA.

---

## Table of Contents

- [Architecture](#architecture)
- [Repository layout](#repository-layout)
- [Development setup](#development-setup)
- [Quality gates](#quality-gates)
- [Security and compliance](#security-and-compliance)
- [Documentation](#documentation)
- [Licence](#licence)

---

## Architecture

- **Framework**: FastAPI on Python 3.12
- **Database**: Multi-tenant Postgres with per-tenant schemas and row-level security
- **Migrations**: Alembic (under `app/db/migrations/`)
- **CRM**: Bitrix24 on-prem REST API (webhooks + client service)
- **Payments**: Stripe (checkout, webhooks) + Paysera (callbacks)
- **AI**: RAG pastoral assistant (LLM with guardrails, assessment, quotes engine)
- **GIS**: Cemetery mapping with geospatial queries
- **Deployment**: Docker + Kubernetes (k3s on Proxmox), Argo CD for GitOps
- **Consumers**: viavitae-web (Next.js), demo templates, client portals

## Repository layout

```text
viavitae-api/
+-- README.md                     # This file
+-- LICENSE                       # Proprietary - All Rights Reserved, EU/LT jurisdiction
+-- SECURITY.md                   # Disclosure policy, SLA table, safe harbour, scope
+-- QODER.md                      # Behavioural guidelines for AI-assisted coding
+-- CONTRIBUTING.md               # Contribution workflow, PR rules, DCO sign-off
+-- CHANGELOG.md                  # Keep a Changelog driven by Conventional Commits
+-- pyproject.toml                # Project metadata, dependencies, tool config
+-- uv.lock                       # Pinned dependency lockfile (uv)
+-- alembic.ini                   # Alembic migration config
+-- Dockerfile                    # Production container image
+-- docker-compose.yml            # Local dev environment (Postgres, Keycloak)
+-- .env.example                  # Environment variable template (no real secrets)
+-- .github/
|   +-- CODEOWNERS                # Owner mapping, R2 baseline
|   +-- dependabot.yml            # Weekly grouped updates (pip + github-actions)
|   +-- workflows/
|       +-- ci.yml                # Lint, typecheck, test, SAST, dependency scan
|       +-- compliance-check.yml  # Secrets, licences, governance file presence
|       +-- codeql.yml            # Static analysis (Python)
|       +-- deploy.yml            # Container build and push
|       +-- nightly-e2e.yml       # Nightly end-to-end test schedule
|       +-- openapi-diff.yml      # Breaking-change detection on /v1 contract
+-- app/
|   +-- core/                     # Config, errors, lifecycle, logging, pagination,
|   |                             # rate limiting, security headers, tenancy
|   +-- api/v1/                   # Route handlers (health, AI, assessment, CRM,
|   |   +-- webhooks/             # Bitrix24, Stripe, Paysera webhook handlers
|   +-- db/                       # Session, Alembic migrations
|   +-- models/                   # SQLAlchemy models
|   +-- services/                 # Business logic (bitrix24, payments, rag)
|   +-- workers/                  # Background tasks
+-- scripts/                      # Dev ops: migrations, OpenAPI export, tenant provisioning
+-- tests/                        # api/, unit/, contract/, isolation/, security/, webhooks/
+-- deployments/                  # k8s manifests, k6 load tests
+-- docs/
    +-- architecture.md           # MADR architecture decision records
    +-- DPIA-template.md          # GDPR Article 35 assessment template
    +-- DPIA-002-ai-pastoral-assistant.md
    +-- DPIA-003-gis-cemetery-map.md
    +-- DPIA-004-donations.md
    +-- data-model.md
    +-- api/                      # OpenAPI spec, versioning policy
    +-- runbooks/                 # Operational runbooks
```

## Development setup

```bash
cp .env.example .env   # fill in local values (never commit .env)
docker compose up -d   # Postgres + Keycloak
uv sync --extra dev    # install dependencies
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## Quality gates

Every pull request must pass:

| Gate | Tool | Threshold |
| --- | --- | --- |
| Lint | `ruff check`, `ruff format` | zero findings |
| Types | `mypy --strict` | zero errors |
| Unit tests | `pytest` | pass, coverage at least 80% |
| Import architecture | `import-linter` | contract preserved |
| SAST | Semgrep, CodeQL | zero findings at or above the failure severity |
| Dependencies | Trivy filesystem | fail on `CRITICAL` |
| Secrets | Gitleaks, full history | fail on any finding |
| Licences | allow-list scan | unknown licence fails and is labelled for review |
| Governance | presence checks | all required files present and non-empty |
| OpenAPI contract | `openapi-diff.yml` | no breaking changes to /v1 paths |

## Security and compliance

- To report a vulnerability, follow the private disclosure process in
  [SECURITY.md](SECURITY.md). Do **not** open a public issue. Acknowledgement is within
  24 hours, triage within 72 hours.
- Personal-data processing requires a completed DPIA under GDPR Article 35 before
  processing starts (R5). See `docs/DPIA-002-*`, `DPIA-003-*`, `DPIA-004-*`.
- Multi-tenant isolation is enforced at the database level (per-tenant schemas + RLS)
  and verified by `tests/isolation/`.
- No PII in logs: `tests/security/test_no_pii_in_logs.py` enforces this.
- A GDPR personal-data breach is notified to the supervisory authority within 72 hours
  of awareness; see the breach workflow in [SECURITY.md](SECURITY.md).

## Documentation

| Document | Purpose |
| --- | --- |
| [SECURITY.md](SECURITY.md) | Disclosure policy, SLA table, safe harbour, scope. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution workflow, PR rules, DCO sign-off. |
| [CHANGELOG.md](CHANGELOG.md) | Release history in Keep a Changelog format. |
| [QODER.md](QODER.md) | AI pair-programming guardrails and stop-conditions. |
| [docs/architecture.md](docs/architecture.md) | MADR decision records and index. |
| [docs/DPIA-template.md](docs/DPIA-template.md) | GDPR Article 35 assessment template. |
| [docs/data-model.md](docs/data-model.md) | Entity relationship and tenancy model. |
| [docs/api/versioning-policy.md](docs/api/versioning-policy.md) | API versioning contract. |

## Licence

Proprietary — All Rights Reserved. (c) ViaVitae IT Technologies. No redistribution, no
derivative works and no commercial use by third parties without a written agreement.
Governed by the law of Lithuania (EU). See [LICENSE](LICENSE).
