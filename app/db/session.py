"""Async SQLAlchemy engine, sessions and tenant context.

Tenant isolation (ADR-004): the tenant id is pushed into the PostgreSQL session
(`SET app.tenant_id`) so row-level security policies can filter rows even if
application code forgets a `WHERE tenant_id = ...` clause.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger, tenant_id_ctx

logger = get_logger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_engine(url: str | Any = None) -> AsyncEngine:
    """Create the engine and session factory once at startup."""
    global _engine, _session_factory
    if _engine is not None:
        return _engine

    database_url = str(url or settings.database_url.get_secret_value())
    _engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        poolclass=NullPool if settings.environment == "dev" else None,
        connect_args={"options": f"-c statement_timeout={settings.statement_timeout_ms}"},
    )
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    logger.info("db.engine_created", environment=settings.environment)
    return _engine


async def close_engine() -> None:
    """Dispose of the engine on shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a tenant-scoped session."""
    if _session_factory is None:
        await init_engine()
    assert _session_factory is not None

    async with _session_factory() as session:
        tenant_id = tenant_id_ctx.get()
        if tenant_id != "-":
            await session.execute(
                text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
                {"tenant_id": tenant_id},
            )
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def ping() -> bool:
    """Readiness check: one round-trip to PostgreSQL."""
    try:
        async for session in get_session():
            await session.execute(text("SELECT 1"))
        return True
    except Exception as exc:  # pragma: no cover - depends on infrastructure
        logger.warning("db.ping_failed", error=str(exc))
        return False
