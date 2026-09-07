"""Nightly reset of demo tenants to pristine fictional seed data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class ResetOutcome:
    """Result of resetting one demo tenant."""

    tenant_slug: str
    template: str
    started_at: datetime
    finished_at: datetime | None
    ok: bool
    error: str = ""


async def reset_tenant(template: str, tenant_slug: str) -> ResetOutcome:
    """Restore one demo tenant from its template seed.

    Steps: drop tenant schema → recreate → run migrations → load fictional seed
    → warm caches → verify with a smoke check. Demos must never contain real
    personal data, which is why the reset is scheduled and verified nightly
    (`viavitae-demos/.github/workflows/demo-reset-smoke.yml`).
    """
    started = datetime.now(tz=None)
    # TODO(api): implement against viavitae-demos/provisioning and the DB layer.
    _ = (template, tenant_slug)
    return ResetOutcome(
        tenant_slug=tenant_slug,
        template=template,
        started_at=started,
        finished_at=None,
        ok=False,
        error="not implemented",
    )


async def reset_all(templates: list[str]) -> list[ResetOutcome]:
    """Reset every demo tenant, continuing past individual failures."""
    outcomes: list[ResetOutcome] = []
    for template in templates:
        outcomes.append(await reset_tenant(template, f"demo-{template}"))
    return outcomes
