"""Receipt generation and Lithuanian tax handling (PVM, GPM 1.2% designation).

Donations are not VAT-able, so ``vat_minor`` is zero for them and the GPM
designation portion is computed instead; goods/services carry PVM at the
standard rate. Amounts stay in integer minor units end to end.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.quotes_engine import (
    CURRENCY_EUR,
    VAT_RATE_BPS,
    gpm_designation_minor,
)


@dataclass(slots=True, frozen=True)
class Receipt:
    """An issued receipt for a payment or donation."""

    number: str
    tenant_id: str
    donor_reference: str
    amount_minor: int
    vat_minor: int
    currency: str = CURRENCY_EUR
    gpm_designation_minor: int = 0


def build_receipt(
    *, number: str, tenant_id: str, donor_reference: str, amount_minor: int, is_donation: bool
) -> Receipt:
    """Compute the tax treatment for one receipt."""
    if amount_minor < 0:
        raise ValueError("amount_minor cannot be negative")
    vat = 0 if is_donation else round(amount_minor * VAT_RATE_BPS / 10_000)
    gpm = gpm_designation_minor(amount_minor) if is_donation else 0
    return Receipt(
        number=number,
        tenant_id=tenant_id,
        donor_reference=donor_reference,
        amount_minor=amount_minor,
        vat_minor=vat,
        gpm_designation_minor=gpm,
    )


async def render_receipt_pdf(receipt: Receipt) -> bytes:
    """Render a receipt as PDF via :mod:`app.services.pdf` (WeasyPrint)."""
    # TODO(api): load the LT/EN receipt template, render with app.services.pdf,
    #            store the artefact and return its bytes.
    _ = receipt
    raise NotImplementedError("receipt PDF rendering is scaffolded but not implemented")
