# Security & Vulnerability Disclosure — `viavitae-api`

This document is part of the organisation-wide security policy published in the
`.github` repository and applies unchanged to `viavitae-api`.

## Reporting a vulnerability

Please report suspected vulnerabilities **privately**. Do **not** open a public
issue or pull request.

| Channel | Detail |
| --- | --- |
| Email | `security@viavitae.eu` |
| GitHub | *Security → Report a vulnerability* (private vulnerability reporting enabled) |
| PGP | Key published at `https://viavitae.eu/.well-known/pgp-key.txt` |

Include: affected repository and version/commit, steps to reproduce, impact,
and whether the finding is already public.

## Response timeline (SLA)

| Stage | Target |
| --- | --- |
| Acknowledgement | 1 business day |
| Triage + severity | 3 business days |
| Fix or mitigation (Critical/High) | 7 calendar days |
| Fix or mitigation (Medium/Low) | 30 calendar days |
| Coordinated public disclosure | 90 days after confirmed report |

## Scope

In scope: all code, infrastructure-as-code, CI/CD configuration, documentation
and demo tenants operated by ViaVitae. Out of scope: third-party SaaS providers
(Stripe, Paysera, Bitrix24) — report those to the vendor and notify us.

## Safe harbour

We consider security research conducted in good faith to be authorised. We will
not pursue legal action against researchers who: avoid accessing or modifying
other people's data, stop testing once an issue is confirmed, do not use
findings for extortion, and report privately before disclosing publicly.

## Data protection

Personal-data incidents (Article 33 GDPR) follow a separate track: the DPO must
be informed within **24 hours** of discovery so the 72-hour supervisory
authority deadline can be met. See `viavitae-docs/docs/security/incident-runbook.md`.

## Supported versions

Only the default branch and the currently deployed release receive security
fixes. Demo tenants are reset nightly and are out of support scope.
