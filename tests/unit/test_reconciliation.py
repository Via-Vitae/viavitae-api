"""Reconciliation reporting: report-only, never mutates, integer money."""

from __future__ import annotations

from datetime import date

from app.services.payments.reconciliation import (
    Discrepancy,
    DiscrepancyKind,
    ReconciliationReport,
    reconcile,
)


def test_new_report_is_clean_and_empty() -> None:
    report = ReconciliationReport(period=date(2026, 9, 1))
    assert report.matched == 0
    assert report.discrepancies == []
    assert report.clean is True


def test_report_with_discrepancy_is_not_clean() -> None:
    report = ReconciliationReport(period=date(2026, 9, 1))
    report.discrepancies.append(
        Discrepancy(
            kind=DiscrepancyKind.AMOUNT_MISMATCH,
            provider_reference="ch_1",
            detail="off by one minor unit",
            amount_minor=1,
        )
    )
    assert report.clean is False
    assert report.discrepancies[0].kind is DiscrepancyKind.AMOUNT_MISMATCH


async def test_reconcile_scaffold_returns_an_empty_report() -> None:
    report = await reconcile(date(2026, 9, 1))
    assert isinstance(report, ReconciliationReport)
    assert report.matched == 0
    assert report.clean is True
