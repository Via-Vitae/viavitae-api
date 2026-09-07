"""Donation intent, history and public impact DTOs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Money, PageMeta


class DonationCreate(BaseModel):
    """A one-off or recurring donation intent."""

    model_config = ConfigDict(extra="forbid")

    amount: Money
    recurring: bool = False
    fund: str | None = Field(default=None, max_length=120)
    donor_reference: str | None = Field(default=None, max_length=120)
    locale: str = Field(default="lt", pattern=r"^(lt|en|ru)$")


class DonationRecord(BaseModel):
    """One donation as shown in the donor portal history."""

    model_config = ConfigDict(frozen=True)

    donation_id: str
    amount: Money
    status: str
    created_at: str
    gpm_designation: Money | None = None


class DonationPage(BaseModel):
    """A cursor-paginated page of donation records."""

    model_config = ConfigDict(frozen=True)

    items: list[DonationRecord]
    page: PageMeta


class ImpactSummary(BaseModel):
    """Aggregated, anonymised impact for the public view (no personal data)."""

    model_config = ConfigDict(frozen=True)

    period: str
    total_raised: Money
    donor_count: int = Field(ge=0)
    causes: list[str] = Field(default_factory=list)
