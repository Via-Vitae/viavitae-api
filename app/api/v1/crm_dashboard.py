"""CRM dashboard metrics: a Bitrix24 pipeline snapshot for client dashboards."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["crm"])


@router.get("/metrics", summary="Bitrix24 pipeline snapshot for the current tenant.")
async def get_metrics() -> dict[str, object]:
    """Return lead/deal counts and stage conversion for the resolved tenant.

    TODO(api): read from the CRM sync cache (app.services.bitrix24.sync) scoped to
    the resolved tenant; never call Bitrix24 synchronously on a dashboard hit.
    """
    raise NotImplementedError("get_metrics is scaffolded but not implemented")
