"""Cursor (keyset) pagination helpers.

Offset pagination leaks total row counts and degrades on large tables, so every
list endpoint paginates with an opaque cursor over a stable sort key
(``created_at`` then ``id``). Clients treat the cursor as opaque; the service
never trusts it beyond decoding a keyset position.
"""

from __future__ import annotations

import base64
import binascii
import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


@dataclass(slots=True, frozen=True)
class Page[T]:
    """One page of results plus the cursor for the next page, if any."""

    items: tuple[T, ...]
    next_cursor: str | None
    limit: int

    @property
    def has_more(self) -> bool:
        """True when a further page exists."""
        return self.next_cursor is not None

    def to_dict(self) -> dict[str, Any]:
        """Serialise the page envelope returned by list endpoints."""
        return {
            "items": list(self.items),
            "page": {
                "next_cursor": self.next_cursor,
                "limit": self.limit,
                "has_more": self.has_more,
            },
        }


def clamp_limit(requested: int | None) -> int:
    """Bound a client-supplied page size to a safe range."""
    if requested is None or requested <= 0:
        return DEFAULT_LIMIT
    return min(requested, MAX_LIMIT)


def encode_cursor(sort_key: str, row_id: str) -> str:
    """Encode a keyset position as an opaque, URL-safe cursor."""
    raw = json.dumps({"k": sort_key, "id": row_id}, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(cursor: str | None) -> tuple[str, str] | None:
    """Decode a cursor; malformed input means 'start from the beginning'."""
    if not cursor:
        return None
    padding = "=" * (-len(cursor) % 4)
    try:
        data = json.loads(base64.urlsafe_b64decode(cursor + padding))
    except (binascii.Error, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    key, row_id = data.get("k"), data.get("id")
    if isinstance(key, str) and isinstance(row_id, str):
        return key, row_id
    return None


def build_page[T](
    items: Sequence[T], *, limit: int, key_fn: Callable[[T], tuple[str, str]]
) -> Page[T]:
    """Build a page from up to ``limit + 1`` fetched rows.

    The caller fetches one extra row to detect whether another page exists
    without a separate COUNT query; ``key_fn`` extracts the sort key of the last
    returned row to form the next cursor.
    """
    has_more = len(items) > limit
    page_items = tuple(items[:limit])
    next_cursor: str | None = None
    if has_more and page_items:
        next_cursor = encode_cursor(*key_fn(page_items[-1]))
    return Page(items=page_items, next_cursor=next_cursor, limit=limit)
