"""Quote request/response DTOs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Money

TIER_PATTERN = r"^(essential|standard|premium)$"


class QuoteRequest(BaseModel):
    """A pricing request for one tier with optional extras."""

    model_config = ConfigDict(extra="forbid")

    tier: str = Field(pattern=TIER_PATTERN)
    extra_seats: int = Field(default=0, ge=0, le=1000)
    annual_prepay: bool = False


class QuoteLine(BaseModel):
    """One priced line on a quote."""

    model_config = ConfigDict(frozen=True)

    description: str
    unit: Money
    quantity: int = Field(ge=0)
    recurring: bool = False
    total: Money


class QuoteResult(BaseModel):
    """A priced quote with its totals and an optional rendered PDF reference."""

    model_config = ConfigDict(frozen=True)

    quote_id: str
    tier: str
    lines: list[QuoteLine]
    one_off_total: Money
    monthly_total: Money
    vat_total: Money
    grand_total: Money
    pdf_url: str | None = None
