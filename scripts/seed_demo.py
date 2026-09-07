#!/usr/bin/env python3
"""Seed a demo tenant with synthetic, entirely fictional data.

Nothing here is real: parishes, people, amounts and references are invented for
local development and demos. The generator is deterministic -- no RNG, no wall
clock -- so two runs produce byte-identical output. That matters for reproducible
demos and for diffing a seeded tenant against a golden copy.

By default the script prints the payload it would write (dry run). ``--apply``
is refused with an explicit reason until the first Alembic revision exists; it
never pretends to have written rows (ADR-004).

Usage::

    python scripts/seed_demo.py                  # print the fictional dataset
    python scripts/seed_demo.py --tenant demo-a  # choose the tenant slug
    python scripts/seed_demo.py --apply          # refused until migrations land
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from app.core.tenancy import schema_for

_VERSIONS_DIR = Path("app/db/migrations/versions")


def build_dataset(tenant: str) -> dict[str, Any]:
    """Return the fictional demo dataset for ``tenant`` as plain data."""
    schema = schema_for(tenant)  # validates the slug exactly as production does
    return {
        "tenant": tenant,
        "schema": schema,
        "locale": "lt",
        "note": "Synthetic demo data. All names and amounts are fictional.",
        # Money is integer minor units (euro cents); floats are never used.
        "assessments": [
            {
                "reference": "DEMO-ASM-0001",
                "score": 62,
                "recommended_tier": "standard",
                "utm": {"utm_source": "demo", "utm_medium": "web", "utm_campaign": "launch"},
            },
            {
                "reference": "DEMO-ASM-0002",
                "score": 88,
                "recommended_tier": "premium",
                "utm": {"utm_source": "demo", "utm_medium": "email"},
            },
        ],
        "quotes": [
            {
                "reference": "DEMO-QT-0001",
                "tier": "standard",
                "one_off_minor": 1900_00,
                "monthly_minor": 40_00,
            },
            {
                "reference": "DEMO-QT-0002",
                "tier": "premium",
                "one_off_minor": 2900_00,
                "monthly_minor": 50_00,
            },
        ],
        "donations": [
            {
                "reference": "DEMO-DON-0001",
                "amount_minor": 25_00,
                "fund": "general",
                "anonymous": True,
            },
            {
                "reference": "DEMO-DON-0002",
                "amount_minor": 100_00,
                "fund": "cemetery-care",
                "anonymous": True,
            },
        ],
    }


def _migrations_present() -> bool:
    """True when at least one Alembic revision exists to create tables."""
    return _VERSIONS_DIR.is_dir() and any(
        path.suffix == ".py" and path.name != "__init__.py" for path in _VERSIONS_DIR.iterdir()
    )


def main(argv: list[str] | None = None) -> int:
    """Entry point; returns a process exit code."""
    parser = argparse.ArgumentParser(description="Generate the fictional demo dataset.")
    parser.add_argument("--tenant", default="demo-a", help="demo tenant slug (default: demo-a)")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write to the database instead of printing (requires migrations)",
    )
    args = parser.parse_args(argv)

    try:
        dataset = build_dataset(args.tenant)
    except Exception as exc:  # InvalidTenantError and any slug problem
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.apply:
        if not _migrations_present():
            print(
                "refusing --apply: no Alembic revisions exist yet, so there are no\n"
                "tables to seed. Run scripts/create_migration.sh first, then retry.",
                file=sys.stderr,
            )
            return 2
        print(
            "refusing --apply: the persistence layer is still scaffolded\n"
            "(NotImplementedError). Dry-run output is printed below; wiring --apply\n"
            "lands with the first migration and repository implementation.",
            file=sys.stderr,
        )
        print(json.dumps(dataset, indent=2, sort_keys=True, ensure_ascii=False))
        return 2

    print(json.dumps(dataset, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
