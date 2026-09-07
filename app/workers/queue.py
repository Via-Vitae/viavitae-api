"""RQ (Redis) queue wiring and priority lanes.

Queues are separated by criticality so a bulk re-index can never starve a
payment webhook handler. Without Redis (dev and the CI unit job) enqueue degrades
to an explicit no-op result rather than raising, so callers stay exercisable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Queue(StrEnum):
    """Priority lanes, highest criticality first."""

    CRITICAL = "vv:critical"  # payment webhooks, receipts
    DEFAULT = "vv:default"  # CRM sync, notifications
    BULK = "vv:bulk"  # RAG re-index, reconciliation, demo reset


@dataclass(slots=True, frozen=True)
class EnqueueResult:
    """Outcome of an enqueue attempt."""

    job_id: str | None
    queue: Queue
    enqueued: bool
    reason: str = ""


def redis_configured() -> bool:
    """True when a Redis URL is present (queues are available)."""
    return settings.redis_url is not None


async def enqueue(queue: Queue, job: str, **kwargs: Any) -> EnqueueResult:
    """Enqueue a job on a priority lane; degrade to a no-op without Redis."""
    if not redis_configured():
        logger.warning("queue.redis_not_configured", queue=queue.value, job=job)
        return EnqueueResult(None, queue, False, "redis not configured")
    # TODO(api): connect via redis.asyncio, RQ Queue(queue).enqueue(job, **kwargs),
    #            return the RQ job id, and set the result TTL and retry policy.
    _ = kwargs
    raise NotImplementedError("queue enqueue is scaffolded but not implemented")
