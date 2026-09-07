"""Cemetery parcels, spatial search and reservation (DPIA-003)."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.schemas.gis import Parcel, ParcelPage, Reservation, ReservationCreate

router = APIRouter(tags=["gis"])


@router.get(
    "/parcels",
    response_model=ParcelPage,
    summary="Search parcels by geometry, section or availability.",
)
async def search_parcels() -> ParcelPage:
    """Consent-gated parcel search; geometry is withheld without consent."""
    raise NotImplementedError("search_parcels is scaffolded but not implemented")


@router.get(
    "/parcels/{parcel_id}", response_model=Parcel, summary="Parcel detail with status history."
)
async def get_parcel(parcel_id: str) -> Parcel:
    """Parcel detail for the resolved tenant."""
    raise NotImplementedError("get_parcel is scaffolded but not implemented")


@router.post(
    "/reservations",
    response_model=Reservation,
    status_code=status.HTTP_201_CREATED,
    summary="Reserve a parcel (idempotent).",
)
async def reserve_parcel(body: ReservationCreate) -> Reservation:
    """Reserve a parcel, idempotent on the supplied key (ADR-005)."""
    raise NotImplementedError("reserve_parcel is scaffolded but not implemented")
