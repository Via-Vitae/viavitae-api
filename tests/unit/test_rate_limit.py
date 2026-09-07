"""Rate limiter with the in-memory backend (offline and deterministic)."""

from __future__ import annotations

from app.core.rate_limit import InMemoryBackend, RateLimiter


class _BrokenBackend:
    """A backend that always fails, to exercise outage behaviour."""

    async def incr_window(self, key: str, window_seconds: int) -> tuple[int, float]:
        raise RuntimeError("redis down")


async def test_allows_up_to_limit_then_denies() -> None:
    limiter = RateLimiter(limit=3, window_seconds=60, backend=InMemoryBackend())
    decisions = [await limiter.check(key="ip:1.2.3.4") for _ in range(4)]
    assert [decision.allowed for decision in decisions] == [True, True, True, False]
    assert decisions[3].remaining == 0


async def test_tenants_are_scoped_independently() -> None:
    limiter = RateLimiter(limit=1, window_seconds=60, backend=InMemoryBackend())
    assert (await limiter.check(key="k", tenant_id="anne")).allowed
    assert not (await limiter.check(key="k", tenant_id="anne")).allowed
    assert (await limiter.check(key="k", tenant_id="bob")).allowed


async def test_fail_open_allows_when_backend_errors() -> None:
    limiter = RateLimiter(limit=5, backend=_BrokenBackend(), fail_open=True)
    assert (await limiter.check(key="k")).allowed


async def test_fail_closed_denies_when_backend_errors() -> None:
    limiter = RateLimiter(limit=5, backend=_BrokenBackend(), fail_open=False)
    assert not (await limiter.check(key="k")).allowed
