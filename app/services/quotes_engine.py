"""Pricing engine: tier selection, quote calculation and margin model.

Money is handled as integer minor units (euro cents) with an explicit currency
code -- never floats -- so totals are exact and auditable (ADR-006). Setup prices
and monthly bands are the published Viavitae tiers; VAT is Lithuanian PVM.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

CURRENCY_EUR = "EUR"
VAT_RATE_BPS = 2100  # Lithuanian PVM 21%, in basis points
GPM_DESIGNATION_BPS = 120  # 1.2% GPM designation on donations
EXTRA_SEAT_MINOR = 5_00  # EUR 5.00 per additional seat, recurring


class Tier(StrEnum):
    """The three published subscription tiers."""

    ESSENTIAL = "essential"
    STANDARD = "standard"
    PREMIUM = "premium"


@dataclass(slots=True, frozen=True)
class TierPlan:
    """Published price point for one tier."""

    tier: Tier
    setup_minor: int
    monthly_minor: int
    included_seats: int


TIERS: dict[Tier, TierPlan] = {
    Tier.ESSENTIAL: TierPlan(Tier.ESSENTIAL, 900_00, 30_00, 3),
    Tier.STANDARD: TierPlan(Tier.STANDARD, 1900_00, 40_00, 10),
    Tier.PREMIUM: TierPlan(Tier.PREMIUM, 2900_00, 50_00, 25),
}


@dataclass(slots=True, frozen=True)
class LineItem:
    """One priced line; ``recurring`` lines are billed monthly."""

    description: str
    unit_minor: int
    quantity: int
    recurring: bool = False

    @property
    def total_minor(self) -> int:
        """Extended price in minor units (negative for credits)."""
        return self.unit_minor * self.quantity


@dataclass(slots=True, frozen=True)
class Quote:
    """A priced quote: one-off setup plus recurring subscription lines."""

    tier: Tier
    items: tuple[LineItem, ...]
    currency: str = CURRENCY_EUR

    @property
    def one_off_minor(self) -> int:
        return sum(item.total_minor for item in self.items if not item.recurring)

    @property
    def monthly_minor(self) -> int:
        return sum(item.total_minor for item in self.items if item.recurring)

    @property
    def vat_minor(self) -> int:
        """PVM on the taxable total, rounded to the nearest minor unit."""
        taxable = self.one_off_minor + self.monthly_minor
        return round(taxable * VAT_RATE_BPS / 10_000)

    @property
    def total_minor(self) -> int:
        return self.one_off_minor + self.monthly_minor + self.vat_minor


def recommend_tier(score: int) -> Tier:
    """Map an assessment score (0-100) to the recommended tier."""
    if not 0 <= score <= 100:
        raise ValueError("assessment score must be within 0..100")
    if score < 40:
        return Tier.ESSENTIAL
    if score < 75:
        return Tier.STANDARD
    return Tier.PREMIUM


def price_quote(tier: Tier, *, extra_seats: int = 0) -> Quote:
    """Build a quote for a tier with optional extra seats.

    Setup is a one-off line; the subscription and any extra seats are recurring
    monthly lines. VAT (PVM) is added on top by the ``Quote`` totals.
    """
    if extra_seats < 0:
        raise ValueError("extra_seats cannot be negative")
    plan = TIERS[tier]
    items: list[LineItem] = [
        LineItem(f"{tier.value} platform setup", plan.setup_minor, 1),
        LineItem(f"{tier.value} monthly subscription", plan.monthly_minor, 1, recurring=True),
    ]
    if extra_seats:
        items.append(LineItem("additional seat", EXTRA_SEAT_MINOR, extra_seats, recurring=True))
    return Quote(tier=tier, items=tuple(items))


def margin_minor(price_minor: int, cost_minor: int) -> int:
    """Gross margin in minor units; a negative margin is surfaced, not hidden."""
    return price_minor - cost_minor


def gpm_designation_minor(donation_minor: int) -> int:
    """The 1.2% GPM designation portion of a donation, in minor units."""
    return round(donation_minor * GPM_DESIGNATION_BPS / 10_000)
