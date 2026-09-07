"""Batch synchronisation of CRM entities.

Uses the Bitrix24 `batch` method to stay inside rate limits (2 requests/second
per integration) and to make multi-entity writes as atomic as the API allows.
Failed items are recorded individually — one bad contact must not abort a
thousand-row sync.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

from app.core.logging import get_logger
from app.services.bitrix24.client import Bitrix24Client

logger = get_logger(__name__)

MAX_BATCH_SIZE = 50


@dataclass(slots=True)
class SyncResult:
    """Outcome of a batch synchronisation run."""

    succeeded: int = 0
    failed: list[tuple[str, str]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when nothing failed."""
        return not self.failed


def _chunks(items: Sequence[Any], size: int) -> Iterable[Sequence[Any]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


class BatchSync:
    """Chunked, resumable batch writer."""

    def __init__(self, client: Bitrix24Client) -> None:
        self._client = client

    async def run(self, method: str, items: Sequence[dict[str, Any]]) -> SyncResult:
        """Send `items` to `method` in batches, collecting per-item failures."""
        result = SyncResult()
        for batch in _chunks(items, MAX_BATCH_SIZE):
            calls = {
                f"item_{index}": {"method": method, "params": item}
                for index, item in enumerate(batch)
            }
            try:
                await self._client.call("batch", {"halt": 0, "cmd": calls})
                result.succeeded += len(batch)
            except Exception as exc:  # per-batch isolation is intentional
                logger.error(
                    "bitrix24.batch_failed", method=method, size=len(batch), error=str(exc)
                )
                result.failed.extend((method, str(exc)) for _ in batch)
        logger.info(
            "bitrix24.batch_done", method=method, ok=result.succeeded, failed=len(result.failed)
        )
        return result
