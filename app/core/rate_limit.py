"""Request rate limiting (per key and per tenant).

A fixed-window counter is kept in Redis in production; an in-memory backend is
used for tests and single-process dev so the limiter is exercisable offline
without a live Redis. The backend is injected, which keeps this module free of
any hard Redis dependency and makes the decision logic unit-testable.

Outage behaviour is explicit: if the counter backend errors, ``fail_open``
decides whether traffic is allowed (default, availability-first for a public
funnel) or denied (``fail_open=False`` for money-moving endpoints).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True, frozen=True)
class RateLimitDecision:
    """Outcome of one rate-limit check."""

    allowed: bool
    limit: int
    remaining: int
    reset_after: float


class CounterBackend(Protocol):
    """A fixed-window counter store."""

    async def incr_window(self, key: str, window_seconds: int) -> tuple[int, float]:
        """Increment the current window; return ``(count, seconds_to_reset)``."""
        ...


class InMemoryBackend:
    """Process-local fixed-window counter for tests and single-process dev."""

    def __init__(self) -> None:
        self._windows: dict[str, tuple[int, int]] = {}

    async def incr_window(self, key: str, window_seconds: int) -> tuple[int, float]:
        now = int(time.monotonic())
        start = now - (now % window_seconds)
        existing = self._windows.get(key)
        count = 1 if existing is None or existing[0] != start else existing[1] + 1
        self._windows[key] = (start, count)
        return count, float(window_seconds - (now - start))


class _RedisClient(Protocol):
    """The subset of ``redis.asyncio.Redis`` this limiter uses."""

    async def incr(self, key: str) -> int: ...

    async def expire(self, key: str, seconds: int) -> bool: ...


class RedisBackend:
    """Fixed-window counter backed by Redis ``INCR`` + ``EXPIRE``."""

    def __init__(self, redis: _RedisClient) -> None:
        self._redis = redis

    async def incr_window(self, key: str, window_seconds: int) -> tuple[int, float]:
        now = int(time.time())
        window = now - (now % window_seconds)
        redis_key = f"ratelimit:{key}:{window}"
        count = int(await self._redis.incr(redis_key))
        if count == 1:
            await self._redis.expire(redis_key, window_seconds)
        return count, float(window_seconds - (now - window))


class RateLimiter:
    """Fixed-window limiter scoped by tenant and caller-supplied key."""

    def __init__(
        self,
        limit: int,
        window_seconds: int = 60,
        backend: CounterBackend | None = None,
        *,
        fail_open: bool = True,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.backend: CounterBackend = backend or InMemoryBackend()
        self.fail_open = fail_open

    async def check(self, *, key: str, tenant_id: str | None = None) -> RateLimitDecision:
        """Return the decision for one request in the current window."""
        scope = f"{tenant_id or 'anon'}:{key}"
        try:
            count, reset_after = await self.backend.incr_window(scope, self.window_seconds)
        except Exception:  # outage handling is deliberate; see fail_open above
            if not self.fail_open:
                return RateLimitDecision(False, self.limit, 0, float(self.window_seconds))
            return RateLimitDecision(True, self.limit, self.limit, float(self.window_seconds))
        allowed = count <= self.limit
        remaining = max(0, self.limit - count)
        return RateLimitDecision(allowed, self.limit, remaining, reset_after)
