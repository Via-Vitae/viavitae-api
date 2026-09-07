"""Alembic environment: multi-schema (schema-per-tenant) migration runner.

Reads the database URL from application settings (never from alembic.ini) and
targets the shared metadata so ``--autogenerate`` sees every model. Migrations
are expand-contract and must include the RLS policy changes for tenant-scoped
tables.

Tenancy model (ADR-004): the control schema (``public``) holds the alembic
version table; each tenant has its own schema. Apply shared/control revisions
with ``alembic upgrade head``, then replay tenant-scoped revisions per schema
with ``alembic upgrade head -x tenant_schema=tenant_<slug>`` (the pattern used by
``scripts/provision_tenant.py``). Passing the schema via ``-x`` avoids building
DDL/search_path strings from input.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from app.core.config import settings
from app.models.base import Base
from sqlalchemy import engine_from_config, pool

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.database_url.get_secret_value())
target_metadata = Base.metadata

CONTROL_SCHEMA = "public"


def _target_schema() -> str | None:
    """Return the tenant schema from ``-x tenant_schema=...``, or None for control."""
    return context.get_x_argument(as_dictionary=True).get("tenant_schema")


def run_migrations_offline() -> None:
    """Emit SQL to stdout without a live connection (CI diffing)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        version_table_schema=CONTROL_SCHEMA,
        schema=_target_schema(),
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database, scoped to the target schema."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True,
            version_table_schema=CONTROL_SCHEMA,
            schema=_target_schema(),
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
