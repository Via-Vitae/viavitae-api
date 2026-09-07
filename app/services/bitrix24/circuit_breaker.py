"""Circuit breaker for outbound CRM calls.

States: `closed` (normal) → `open` (fail fast after a threshold) → `half-open`
(one probe request allowed). Keeps a slow or failing Bitrix24 from exhausting the
API's request budget.
"""

from __future__ import annotations

import asyncio
import time
from enum import StrEnum
from typing import Self

from app.core.logging import get_logger

logger = get_logger(__name__)


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"


class CircuitOpenError(RuntimeError):
    """Raised when the circuit is open and the call is rejected immediately."""

    def __init__(self, name: str, retry_after: float) -> None:
        super().__init__(f"circuit '{name}' is open; retry in {retry_after:.1f}s")
        self.name = name
        self.retry_after = retry_after


class CircuitBreaker:
    """Failure-counting breaker with a recovery window."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_seconds: float = 30.0,
        success_threshold: int = 2,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self.success_threshold = success_threshold
        self.state = CircuitState.CLOSED
        self._failures = 0
        self._successes = 0
        self._opened_at = 0.0
        self._lock = asyncio.Lock()

    def _trip(self) -> None:
        self.state = CircuitState.OPEN
        self._opened_at = time.monotonic()
        self._successes = 0
        logger.warning("circuit.open", breaker=self.name, failures=self._failures)

    def _reset(self) -> None:
        self.state = CircuitState.CLOSED
        self._failures = 0
        self._successes = 0
        logger.info("circuit.closed", breaker=self.name)

    async def __aenter__(self) -> Self:
        async with self._lock:
            if self.state is CircuitState.OPEN:
                elapsed = time.monotonic() - self._opened_at
                if elapsed < self.recovery_seconds:
                    raise CircuitOpenError(self.name, self.recovery_seconds - elapsed)
                self.state = CircuitState.HALF_OPEN
                self._successes = 0
                logger.info("circuit.half_open", breaker=self.name)
        return self

    async def __aexit__(self, exc_type: object, _exc: object, _tb: object) -> bool:
        async with self._lock:
            if exc_type is None:
                self._failures = 0
                if self.state is CircuitState.HALF_OPEN:
                    self._successes += 1
                    if self._successes >= self.success_threshold:
                        self._reset()
                return False

            self._failures += 1
            if self._failures >= self.failure_threshold or self.state is CircuitState.HALF_OPEN:
                self._trip()
            return False
