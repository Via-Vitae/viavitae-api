# DPIA-XXX — <short title>

Data Protection Impact Assessment. Complete one DPIA per processing activity
before it goes live. Store completed assessments next to this template as
`DPIA-<number>-<slug>.md` and index them in `viavitae-docs/docs/gdpr/ropa.md`.

| Field | Value |
| --- | --- |
| DPIA number | DPIA-XXX |
| Repository | viavitae-api |
| Controller | ViaVitae (and the client tenant where applicable) |
| Activity owner | |
| DPO / reviewer | |
| Date created | |
| Date of last review | |
| Status | draft / in review / approved / superseded |

## 1. Description of the processing

- What is processed, by whom, for which purpose?
- Data categories (identify personal, special category Art. 9, children's data).
- Data subjects and approximate volume.
- Source of the data.
- Systems, services and sub-processors involved, with their hosting region.

## 2. Necessity and proportionality

- Why is this processing necessary for the stated purpose?
- Which less intrusive alternatives were considered and rejected?
- Data minimisation: which fields were dropped and why?
- Retention period and the deletion mechanism (automatic or runbook).
- Legal basis (Art. 6) and, where relevant, Art. 9(2) condition.

## 3. Risks to data subjects

| # | Risk | Likelihood | Severity | Inherent risk |
| --- | --- | --- | --- | --- |
| R1 | | | | |
| R2 | | | | |

Consider: unauthorised access, loss of confidentiality, data loss, inaccurate
data leading to wrong decisions, discrimination, reputational damage for the
Church context (religious belief is a special category under Art. 9 GDPR).

## 4. Measures to mitigate risks

| # | Risk | Measure | Type (technical / organisational) | Residual risk | Owner | Due |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | R1 | | | | | |

Baseline measures already in place: encryption in transit and at rest, RBAC,
tenant isolation, audit logging, EU residency, DPA with every processor,
incident runbook, DSR procedure.

## 5. Consultation

- Data subjects or their representatives consulted? Outcome?
- Processor consulted?
- Prior consultation with the supervisory authority required (Art. 36)? Yes/No,
  and if yes, date and reference.

## 6. Outcome and sign-off

- Residual risk acceptable? Justify.
- Conditions attached to the approval.
- Review trigger: change of purpose, new processor, new data category, incident,
  or 12 months — whichever comes first.

| Role | Name | Date | Signature |
| --- | --- | --- | --- |
| Activity owner | | | |
| DPO | | | |
| Management | | | |
