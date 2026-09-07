# Runbook — Tenant provisioning

> Backs `scripts/provision_tenant.py`. Tenant isolation uses a shared
> PostgreSQL database with one schema per tenant, enforced by row-level
> security (ADR-004).

## When to use

- A new parish or diocese has been onboarded and needs its own tenant schema.
- A test tenant is needed for staging or integration testing.

## Prerequisites

| Item | Detail |
| --- | --- |
| Tenant slug | Lowercase, DNS-safe (e.g. `anne`, `vilnius-archdiocese`) |
| `DATABASE_URL` | Control-plane DSN with `CREATE SCHEMA` privileges |
| `app_runtime` role | Must exist in PostgreSQL; the DDL grants it access |
| Alembic | Installed in the virtualenv (`uv run alembic`) |

## Steps

### 1. Validate the slug

```bash
python scripts/provision_tenant.py anne --locale lt
```

The script calls `app.core.tenancy.schema_for()` which applies the same
validation and prefix rules the application uses at runtime. If the slug is
invalid (uppercase, special characters, reserved words), the script exits
with code 2 and a clear error.

### 2. Review the emitted command

The script prints two commands — it does **not** execute them:

```bash
# 1. Create the schema and grant privileges
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -v schema="t_anne" <<'SQL'
CREATE SCHEMA IF NOT EXISTS :"schema";
GRANT USAGE ON SCHEMA :"schema" TO app_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA :"schema"
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_runtime;
SQL

# 2. Apply tenant-scoped migrations
alembic -x tenant_schema=t_anne upgrade head
```

The schema name is passed as a `psql` variable (`:"schema"`), never
interpolated into SQL by string concatenation.

### 3. Execute

Run the emitted commands with `DATABASE_URL` set to the control-plane DSN.
`ON_ERROR_STOP=1` ensures a partial failure aborts instead of leaving a
half-created schema.

### 4. Verify

```sql
-- Confirm the schema exists and has the expected tables
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 't_anne';
SELECT table_name FROM information_schema.tables WHERE table_schema = 't_anne';

-- Confirm RLS is enabled on every table
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 't_anne';
```

Every table should show `rowsecurity = true`.

## Naming convention

| Input slug | Schema name | Rationale |
| --- | --- | --- |
| `anne` | `t_anne` | Prefix avoids collision with reserved schemas (`public`, `pg_catalog`) |

The prefix and validation rules are defined in `app/core/tenancy.py` and are
shared between this script and the runtime tenant middleware.

## De-provisioning

To remove a tenant, drop the schema:

```sql
DROP SCHEMA IF EXISTS :"schema" CASCADE;
```

**Warning:** this is irreversible. Ensure backups are current and the tenant
has confirmed deletion. Log the action in the audit trail.
