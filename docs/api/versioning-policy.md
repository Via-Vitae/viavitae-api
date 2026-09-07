# API versioning policy

| Rule | Detail |
| --- | --- |
| Prefix | `/v1` in the path; no version in headers or query strings |
| Contract | `docs/api/v1-openapi.json`, generated from the app and diffed in CI |
| Additive | New optional fields, new endpoints and new enum members are non-breaking |
| Breaking | Removed/renamed fields, new required fields, narrowed enums, changed semantics |
| Breaking → new version | `/v2` is introduced; `/v1` keeps working for ≥ 6 months |
| Deprecation | `Deprecation: true` + `Sunset: <date>` headers, changelog entry, direct client notice |
| Errors | One envelope: `{"error": {"code", "message", "details", "request_id"}}` |
| Idempotency | `Idempotency-Key` required for money-moving and webhook-triggered writes |
| Pagination | Cursor-based (`?cursor=&limit=`), max limit 100 |
| Rate limits | Per tenant; `429` with `Retry-After`; limits documented per endpoint |
| Time & money | ISO 8601 UTC timestamps; amounts as integer minor units + `currency` |

## Breaking-change checklist

- [ ] New version directory created and mounted (`app/api/v2/`).
- [ ] Old version untouched and still tested.
- [ ] Deprecation headers added with a `Sunset` date ≥ 6 months ahead.
- [ ] `CHANGELOG.md` entry under `Deprecated`.
- [ ] Every known consumer notified (web, demos, marketplace, client tenants).
- [ ] Migration guide published in `viavitae-docs/docs/adr/`.
