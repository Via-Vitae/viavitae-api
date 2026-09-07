"""Assessment funnel DTOs (DPIA-001)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Money

LOCALE_PATTERN = r"^(lt|en|ru|pl|de)$"


class UtmParams(BaseModel):
    """Marketing attribution captured with the submission (kept on the CRM lead)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: str | None = Field(default=None, max_length=200)
    medium: str | None = Field(default=None, max_length=200)
    campaign: str | None = Field(default=None, max_length=200)
    term: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None, max_length=200)


class AssessmentSubmit(BaseModel):
    """A completed funnel submission; contact data is minimised (DPIA-001)."""

    model_config = ConfigDict(extra="forbid")

    parish: str = Field(min_length=1, max_length=200)
    congregation_size: int = Field(ge=0, le=1_000_000)
    contact_email: str | None = Field(default=None, max_length=320)
    locale: str = Field(default="lt", pattern=LOCALE_PATTERN)
    utm: UtmParams | None = None


class AssessmentResult(BaseModel):
    """The recommended tier and an indicative monthly price."""

    model_config = ConfigDict(frozen=True)

    assessment_id: str
    score: int = Field(ge=0, le=100)
    recommended_tier: str
    indicative_monthly: Money
