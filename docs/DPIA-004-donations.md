# DPIA-004 — Donations and payment processing

| Field | Value |
| --- | --- |
| DPIA number | 004 |
| Repository | `viavitae-api` |
| Controller | The client church organisation (parish/diocese); ViaVitae is processor |
| Activity owner | _to be assigned_ |
| DPO / reviewer | _to be assigned_ |
| Status | draft — approval required before go-live |

## 1. Description of the processing

Online donation collection via Stripe and Paysera, with receipt generation
and CRM synchronisation to Bitrix24.

| Category | Examples | Special category (Art. 9)? |
| --- | --- | --- |
| Identity | Donor name, email, address | No |
| Financial | Payment amount, currency, method, transaction id | No |
| Contact | Phone number (optional) | No |
| Gift Aid | Tax status declaration (UK only, if applicable) | Possibly — reveals religious affiliation indirectly |

Data subjects, volume, sources, systems and sub-processors:

- **Data subjects:** individual donors to the tenant parish/diocese.
- **Sources:** donor enters data directly via the web frontend; payment
  details are tokenised by Stripe/Paysera and never reach our servers.
- **Storage:** PostgreSQL in the EU region (`viavitae-infra`), tenant-scoped
  with RLS. Payment tokens are ephemeral.
- **Processing location:** k3s cluster on Proxmox, EEA.
- **Sub-processors:** Stripe (EU entity, DPA on file), Paysera (EU, DPA on
  file), Bitrix24 (EU instance, DPA on file).

## 2. Necessity and proportionality

- **Purpose:** process donations on behalf of the controller; legal basis
  Art. 6(1)(b) (contractual — the controller uses ViaVitae to collect
  donations) and Art. 6(1)(c) (legal obligation — tax receipt records).
- **Data minimisation:** only the fields needed for payment processing and
  receipt generation are stored. Card numbers are never stored — Stripe and
  Paysera tokenise at the point of entry.
- **Retention:** donation records retained for 7 years (tax/legal obligation);
  donor contact details deleted on request after the last donation + retention
  period.
- **Alternatives considered:** offloading entirely to Stripe/Paysera — rejected
  because the controller needs unified records across payment methods and CRM
  sync.

## 3. Risks to data subjects

| # | Risk | Likelihood | Severity | Inherent risk |
| --- | --- | --- | --- | --- |
| R1 | Unauthorised cross-tenant access to donor data | Low | High | Medium |
| R2 | Duplicate receipts or payments due to webhook replay | Medium | Medium | Medium |
| R3 | Payment data leakage via logs or error messages | Low | High | Medium |
| R4 | Donor data retained beyond the retention period | Low | Medium | Low |

## 4. Measures

| # | Risk | Measure | Type | Residual risk | Owner | Due |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | R1 | Row-level security on every table; tenant GUC set in code. **STATUS 2026-10-27: PARTIALLY IMPLEMENTED** — `app/db/session.py` does set `app.tenant_id`, but `app/db/migrations/versions/` contains only `.gitkeep` (zero Alembic revisions) and the image never runs `alembic upgrade head`, so no tables and no RLS policies exist; `tests/isolation/*` are skipped TODOs (VV-2026-10-016). The `Low` rating is therefore **not evidenced** | Technical | **Not evidenced** | ViaVitae | Go-live |
| M2 | R2 | Idempotency ledger (ADR-005); webhook signature verification (fail-closed). **STATUS 2026-10-27: NOT IMPLEMENTED** — the handlers are `501` stubs and neither ledger table exists, so this measure does not yet reduce R2 and the `Low` residual rating is **unsupported by evidence** (DPO must re-rate before go-live) | Technical | **Not evidenced** | ViaVitae | Go-live |
| M3 | R3 | Structured logging excludes payment tokens and card data — **verified real**: a `_redact` processor over secret-named keys in `app/core/logging.py`. SAST in CI — **tool corrected**: the `sast` job runs **Semgrep** (`p/security-audit`, `p/secrets`, `p/owasp-top-ten`) and a Trivy filesystem scan runs in `dependency-scan`; `bandit` is only a declared dev dependency, not a CI gate | Organisational | Low | ViaVitae | Go-live |
| M4 | R4 | Retention cron job — **STATUS 2026-10-27: NOT IMPLEMENTED** — the cited `app/workers/retention_worker.py` does not exist (that directory holds `demo_reset`, `followups`, `index_worker`, `queue`, `reconciliation_worker`). The annual DPO review is a process commitment, not a control in code | Organisational | **Not evidenced** | DPO | Q1 after go-live |

Baseline claimed in place: TLS 1.3, encryption at rest, RBAC, tenant RLS,
audit logging, EU residency, incident runbook, DSR procedure.
**Correction (2026-10-27):** *idempotency* was listed here but is **not** in
place — it is the unimplemented M2 above. Read from the code, not from the
docstrings: `app/api/v1/webhooks/*.py` all raise `501 not_implemented`.

## 5. Consultation

- Data subjects / representatives: _donors informed via the controller's
  privacy notice at the point of donation_
- Processor: ViaVitae (DPA signed)
- Art. 36 prior consultation required? **Unresolved — re-assess.** The original
  answer was "No", justified by "measures reduce residual risk to low for all
  identified risks"; that premise fails for R2, whose only mitigation (M2) is not
  implemented. The conclusion itself is a legal determination for the DPO, not an
  engineering one (GDPR Art. 35(7)(d), Art. 36).

## 6. Outcome and sign-off

| Role | Name | Date | Signature |
| --- | --- | --- | --- |
| Activity owner | | | |
| DPO | | | |
| Management | | | |
