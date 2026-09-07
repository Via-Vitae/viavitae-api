"""Pricing engine tests: tier bands, VAT, credits and integer money."""

from __future__ import annotations

import pytest
from app.services.quotes_engine import (
    CURRENCY_EUR,
    TIERS,
    Tier,
    gpm_designation_minor,
    margin_minor,
    price_quote,
    recommend_tier,
)


def test_tier_bands_match_published_prices() -> None:
    """The scaffold must encode the published EUR 900/1900/2900 setup bands."""
    assert TIERS[Tier.ESSENTIAL].setup_minor == 900_00
    assert TIERS[Tier.STANDARD].setup_minor == 1900_00
    assert TIERS[Tier.PREMIUM].setup_minor == 2900_00
    assert TIERS[Tier.ESSENTIAL].monthly_minor == 30_00
    assert TIERS[Tier.PREMIUM].monthly_minor == 50_00


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0, Tier.ESSENTIAL),
        (39, Tier.ESSENTIAL),
        (40, Tier.STANDARD),
        (74, Tier.STANDARD),
        (75, Tier.PREMIUM),
        (100, Tier.PREMIUM),
    ],
)
def test_recommend_tier_thresholds(score: int, expected: Tier) -> None:
    assert recommend_tier(score) is expected


@pytest.mark.parametrize("score", [-1, 101, 1000])
def test_recommend_tier_rejects_out_of_range(score: int) -> None:
    with pytest.raises(ValueError, match="within"):
        recommend_tier(score)


def test_price_quote_totals_are_integer_eur_cents() -> None:
    quote = price_quote(Tier.ESSENTIAL)
    assert quote.currency == CURRENCY_EUR
    assert quote.one_off_minor == 900_00
    assert quote.monthly_minor == 30_00
    # PVM 21% over 93000 minor units == 19530, exactly (no float drift).
    assert quote.vat_minor == 19_530
    assert quote.total_minor == 900_00 + 30_00 + 19_530
    assert all(
        isinstance(value, int)
        for value in (quote.one_off_minor, quote.monthly_minor, quote.vat_minor, quote.total_minor)
    )


def test_price_quote_extra_seats_are_recurring() -> None:
    quote = price_quote(Tier.STANDARD, extra_seats=3)
    assert quote.monthly_minor == 40_00 + 3 * 5_00
    assert quote.one_off_minor == 1900_00


def test_price_quote_rejects_negative_seats() -> None:
    with pytest.raises(ValueError, match="negative"):
        price_quote(Tier.ESSENTIAL, extra_seats=-1)


def test_margin_surfaces_negative_and_gpm_is_exact() -> None:
    assert margin_minor(100_00, 60_00) == 40_00
    assert margin_minor(50_00, 60_00) == -10_00
    assert gpm_designation_minor(100_00) == 1_20  # 1.2% of EUR 100.00
