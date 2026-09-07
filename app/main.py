"""Application entrypoint.

Composition root only: settings, middleware, exception handlers, router mounts
and infrastructure health probes. Business logic lives in ``app/services/`` and
resource lifecycle in ``app/core/lifecycle.py``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.lifecycle import shutdown, startup
from app.core.logging import get_logger, request_id_middleware
from app.core.security_headers import SecurityHeadersMiddleware
from app.db.session import ping

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialise shared resources; tear them down on shutdown."""
    await startup()
    logger.info("api.started", version=settings.app_version)
    try:
        yield
    finally:
        await shutdown()
        logger.info("api.stopped")


def create_app() -> FastAPI:
    """Build the FastAPI application (used by uvicorn and by tests)."""
    app = FastAPI(
        title="ViaVitae API",
        version=settings.app_version,
        docs_url="/docs" if settings.environment != "prod" else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.environment != "prod" else None,
        lifespan=lifespan,
        servers=[{"url": f"https://api.viavitae.eu/{settings.api_prefix}"}],
    )

    register_error_handlers(app)

    # Middleware added last is outermost; request-id wraps everything so every
    # log line and error envelope can be correlated.
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Idempotency-Key",
            "X-Tenant",
            "X-Request-Id",
        ],
    )
    if settings.environment == "prod" and settings.trusted_hosts:
        # Host-header validation in prod (the ingress also enforces it): skipped
        # in dev/test so local hosts and the ASGI test client are not rejected.
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
    app.middleware("http")(request_id_middleware)

    app.include_router(api_router, prefix=f"/{settings.api_prefix}")

    @app.get("/health/live", tags=["health"], include_in_schema=False)
    async def liveness() -> JSONResponse:
        """Liveness probe: no dependency is touched."""
        return JSONResponse({"status": "ok"})

    @app.get("/health/ready", tags=["health"], include_in_schema=False)
    async def readiness() -> JSONResponse:
        """Readiness probe: database reachable."""
        healthy = await ping()
        return JSONResponse(
            {"status": "ok" if healthy else "degraded"},
            status_code=200 if healthy else 503,
        )

    return app


app = create_app()

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    # Local dev only; the container binds 0.0.0.0 via its CMD, not this block.
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
