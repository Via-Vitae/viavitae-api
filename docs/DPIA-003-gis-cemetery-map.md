# DPIA-003 — GPS cemetery map

| Field | Value |
| --- | --- |
| DPIA number | 003 |
| Repository | `viavitae-api` |
| Controller | The client church organisation (parish/diocese); ViaVitae is processor |
| Activity owner | _to be assigned_ |
| DPO / reviewer | _to be assigned_ |
| Status | draft — approval required before go-live |

## 1. Description of the processing

Parcel geometry, burial records and reservation data with precise location.

| Category | Examples | Special category (Art. 9)? |
| --- | --- | --- |
| | | |

Data subjects, volume, sources, systems and sub-processors:

- Storage: PostgreSQL in the EU region (`viavitae-infra`), tenant-scoped with RLS.
- Processing location: k3s cluster on Proxmox, EEA.
- Sub-processors: _list with DPA reference and region_.

## 2. Necessity and proportionality

- Purpose and legal basis (Art. 6, and Art. 9(2) where special category data).
- Data minimisation: which fields are collected and why; which were rejected.
- Retention period and the deletion mechanism.
- Alternatives considered and why they were rejected.

## 3. Risks to data subjects

| # | Risk | Likelihood | Severity | Inherent risk |
| --- | --- | --- | --- | --- |
| R1 | | | | |
| R2 | | | | |

## 4. Measures

| # | Risk | Measure | Type | Residual risk | Owner | Due |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | R1 | | | | | |

Baseline already in place: TLS 1.3, encryption at rest, RBAC, tenant RLS,
audit logging, idempotency, EU residency, incident runbook, DSR procedure.

## 5. Consultation

- Data subjects / representatives:
- Processor:
- Art. 36 prior consultation required? Yes/No — reference:

## 6. Outcome and sign-off

| Role | Name | Date | Signature |
| --- | --- | --- | --- |
| Activity owner | | | |
| DPO | | | |
| Management | | | |
