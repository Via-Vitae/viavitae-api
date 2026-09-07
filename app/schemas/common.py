"""Shared DTOs: the error envelope, pagination metadata and Money(EUR)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.pagination import DEFAULT_LIMIT, MAX_LIMIT

CURRENCY_EUR = "EUR"


class ErrorDetail(BaseModel):
    """The inner error object; ``code`` is stable and machine-readable."""

    model_config = ConfigDict(frozen=True)

    code: str
    message: str
    details: Any = None
    request_id: str | None = None


class Error(BaseModel):
    """The single error shape returned by every failing endpoint (ADR-006)."""

    model_config = ConfigDict(frozen=True)

    error: ErrorDetail


class Money(BaseModel):
    """An amount in integer minor units plus an ISO-4217 currency code.

    Floats are never used for money (ADR-006); EUR is the default and the only
    currency currently supported by the pricing engine.
    """

    model_config = ConfigDict(frozen=True)

    amount_minor: int = Field(description="Amount in minor units (euro cents).")
    currency: str = Field(default=CURRENCY_EUR, pattern=r"^[A-Z]{3}$")


class PageMeta(BaseModel):
    """Cursor pagination metadata returned alongside a list of items."""

    model_config = ConfigDict(frozen=True)

    next_cursor: str | None = None
    limit: int = Field(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)
    has_more: bool = False
