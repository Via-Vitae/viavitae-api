"""Versioned health, readiness and version endpoints (client-facing).

Infrastructure probes use the unauthenticated root ``/health/live`` and
``/health/ready`` (see :mod:`app.main`); these ``/v1`` endpoints are the stable,
client-facing contract and never leak build internals beyond the version. The
readiness check reaches the database only through the ``app.api.deps`` seam so
this router keeps no direct persistence import (import-linter enforced).
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.deps import database_ready
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Shallow liveness signal for API clients.")
async def health() -> dict[str, str]:
    """Return a shallow health signal without touching any dependency."""
    return {"status": "ok", "service": settings.app_name}


@router.get("/ready", summary="Readiness: database reachable.")
async def ready() -> JSONResponse:
    """Report readiness; answer 503 when the database is not reachable."""
    healthy = await database_ready()
    return JSONResponse(
        {"status": "ok" if healthy else "degraded"},
        status_code=200 if healthy else 503,
    )


@router.get("/version", summary="Service name, version and environment.")
async def version() -> dict[str, str]:
    """Return non-sensitive build metadata for clients and dashboards."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }
