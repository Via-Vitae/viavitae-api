"""Cemetery GIS DTOs (consent-gated; DPIA-003)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PageMeta

PARCEL_STATUS_PATTERN = r"^(available|reserved|occupied|held)$"


class Parcel(BaseModel):
    """A cemetery parcel; geometry is GeoJSON and may be withheld without consent."""

    model_config = ConfigDict(frozen=True)

    parcel_id: str
    cemetery_id: str
    section: str
    status: str = Field(pattern=PARCEL_STATUS_PATTERN)
    geometry: dict[str, Any] | None = None


class ParcelPage(BaseModel):
    """A cursor-paginated page of parcels."""

    model_config = ConfigDict(frozen=True)

    items: list[Parcel]
    page: PageMeta


class ReservationCreate(BaseModel):
    """A parcel reservation; consent is recorded server-side, never trusted here."""

    model_config = ConfigDict(extra="forbid")

    parcel_id: str
    idempotency_key: str = Field(min_length=8, max_length=200)


class Reservation(BaseModel):
    """A stored parcel reservation."""

    model_config = ConfigDict(frozen=True)

    reservation_id: str
    parcel_id: str
    status: str
    created_at: str
