"""Reconcile provider statements against local donation records."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class DiscrepancyKind(StrEnum):
    """Categories of mismatch found during reconciliation."""

    MISSING_LOCALLY = "missing_locally"
    MISSING_AT_PROVIDER = "missing_at_provider"
    AMOUNT_MISMATCH = "amount_mismatch"
    CURRENCY_MISMATCH = "currency_mismatch"
    DUPLICATE = "duplicate"
    REFUND_NOT_RECORDED = "refund_not_recorded"


@dataclass(slots=True, frozen=True)
class Discrepancy:
    """A single reconciliation finding, reported but never auto-fixed."""

    kind: DiscrepancyKind
    provider_reference: str
    detail: str
    amount_minor: int | None = None


@dataclass(slots=True)
class ReconciliationReport:
    """Outcome of a daily reconciliation run."""

    period: date
    matched: int = 0
    discrepancies: list[Discrepancy] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        """True when the provider statement matched local records exactly."""
        return not self.discrepancies


async def reconcile(period: date) -> ReconciliationReport:
    """Compare provider payouts with local records for one accounting day.

    Rules:
      * never mutate financial records here - report only;
      * every discrepancy is alerted to finance and stored for audit;
      * amounts are compared in integer minor units, never floats.
    """
    report = ReconciliationReport(period=period)
    # TODO(api): load provider statement + local donations for `period`,
    #            diff by provider_reference, populate report.discrepancies,
    #            and dispatch the finance notification.
    return report
