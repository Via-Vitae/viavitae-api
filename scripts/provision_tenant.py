#!/usr/bin/env python3
"""Provision a new tenant schema (schema-per-tenant isolation, ADR-004).

The script validates the requested slug, derives the PostgreSQL schema name with
exactly the rules the application uses, and emits a *reviewed* provisioning
command. It deliberately does not execute DDL itself: creating a tenant schema is
a privileged, auditable action, so an operator -- or the viavitae-clients merge
pipeline -- runs the emitted command on purpose.

It also never builds SQL by string interpolation. The validated schema name is
passed to ``psql`` as a bound variable and expanded inside the statement as
``:"schema"``, so no untrusted text is concatenated into SQL in this process.

Usage::

    python scripts/provision_tenant.py anne
    python scripts/provision_tenant.py anne --locale lt
"""

from __future__ import annotations

import argparse
import sys

from app.core.tenancy import InvalidTenantError, schema_for

# Constant DDL. psql expands :"schema" from a -v binding; ON_ERROR_STOP makes a
# partial failure abort instead of leaving a half-created schema behind.
_PROVISION_SQL = """\
CREATE SCHEMA IF NOT EXISTS :"schema";
GRANT USAGE ON SCHEMA :"schema" TO app_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA :"schema"
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_runtime;
"""


def provision_lines(schema: str) -> list[str]:
    """Return the provisioning command as printable lines.

    The DDL is emitted verbatim from a constant; only the ``psql`` variable
    binding and the ``alembic -x`` argument carry the (already validated) schema
    name, so nothing is interpolated into a SQL statement.
    """
    return [
        f'psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -v schema="{schema}" <<\'SQL\'',
        _PROVISION_SQL.rstrip("\n"),
        "SQL",
        "",
        "# then apply the tenant-scoped migrations:",
        f"alembic -x tenant_schema={schema} upgrade head",
    ]


def main(argv: list[str] | None = None) -> int:
    """Entry point; returns a process exit code."""
    parser = argparse.ArgumentParser(description="Emit the tenant provisioning command.")
    parser.add_argument("slug", help="tenant slug, e.g. 'anne' (lowercase, DNS-safe)")
    parser.add_argument("--locale", default="lt", help="default locale (informational)")
    args = parser.parse_args(argv)

    try:
        schema = schema_for(args.slug)
    except InvalidTenantError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"# tenant slug : {args.slug}")
    print(f"# schema      : {schema}")
    print(f"# locale      : {args.locale}")
    print("# Run the following with DATABASE_URL set to the control-plane DSN:\n")
    for line in provision_lines(schema):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
