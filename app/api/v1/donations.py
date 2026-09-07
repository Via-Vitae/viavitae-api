"""Donation flow, donor history and public impact aggregation."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.schemas.donation import DonationCreate, DonationPage, DonationRecord, ImpactSummary

router = APIRouter(tags=["donations"])


@router.post(
    "/",
    response_model=DonationRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Create a one-off or recurring donation intent.",
)
async def create_donation_intent(body: DonationCreate) -> DonationRecord:
    """Create a donation intent and hand off to the payment adapter.

    TODO(api): create the checkout via app.services.payments, store the intent
    and return the record. Idempotent on the Idempotency-Key header (ADR-005).
    """
    raise NotImplementedError("create_donation_intent is scaffolded but not implemented")


@router.get(
    "/impact",
    response_model=ImpactSummary,
    summary="Aggregated, anonymised impact for public reporting.",
)
async def get_impact() -> ImpactSummary:
    """Public, aggregated impact figures -- never per-donor personal data."""
    raise NotImplementedError("get_impact is scaffolded but not implemented")


@router.get(
    "/history",
    response_model=DonationPage,
    summary="Donation history for the authenticated donor portal.",
)
async def get_history() -> DonationPage:
    """Cursor-paginated donation history for the authenticated donor."""
    raise NotImplementedError("get_history is scaffolded but not implemented")
