"""Pricing engine and PDF quote generation."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.schemas.quote import QuoteRequest, QuoteResult

router = APIRouter(tags=["quotes"])


@router.post(
    "/",
    response_model=QuoteResult,
    status_code=status.HTTP_201_CREATED,
    summary="Price a configuration of products and services.",
)
async def calculate_quote(body: QuoteRequest) -> QuoteResult:
    """Price a tier configuration via app.services.quotes_engine.

    TODO(api): call quotes_engine.price_quote, render the PDF with
    app.services.pdf (WeasyPrint), push to CRM and email the quote.
    """
    raise NotImplementedError("calculate_quote is scaffolded but not implemented")


@router.get("/tiers", summary="List tiers available for a church type.")
async def list_tiers() -> dict[str, object]:
    """List the published tiers and their price bands.

    TODO(api): return the tier catalogue from app.services.quotes_engine.TIERS.
    """
    raise NotImplementedError("list_tiers is scaffolded but not implemented")


@router.get("/{quote_id}/pdf", summary="Render a stored quote as a signed PDF.")
async def render_quote_pdf(quote_id: str) -> dict[str, object]:
    """Render a stored quote as a signed PDF (WeasyPrint).

    TODO(api): load the quote for the tenant and stream the PDF via
    app.services.pdf; sign/number it per the LT invoicing rules.
    """
    raise NotImplementedError("render_quote_pdf is scaffolded but not implemented")
