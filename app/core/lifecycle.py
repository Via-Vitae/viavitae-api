"""Application lifecycle: startup and graceful shutdown.

Centralising resource setup keeps ``app.main`` a thin composition root and makes
the order explicit -- logging -> database -> redis/scheduler on the way up, and
teardown in reverse. Required dependencies fail fast; optional ones (Redis, the
RQ scheduler) are enabled only when configured, so dev and the CI unit job boot
without them.
"""

from __future__ import annotations

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.session import close_engine, init_engine

logger = get_logger(__name__)


async def startup() -> None:
    """Initialise shared resources; fail fast if a required one is unavailable."""
    configure_logging(settings.log_level, settings.log_json)
    await init_engine(settings.database_url.get_secret_value())
    logger.info("lifecycle.db_ready", environment=settings.environment)
    if settings.redis_url is not None:
        # TODO(api): open the redis.asyncio connection pool and start the RQ
        #            scheduler; both are optional in dev and in the CI unit job.
        logger.info("lifecycle.redis_configured")


async def shutdown() -> None:
    """Release resources in the reverse order of acquisition."""
    await close_engine()
    logger.info("lifecycle.stopped")
