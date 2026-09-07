"""Payment reconciliation worker entrypoint (nightly cronjob).

Reconciles the previous accounting day by default and logs discrepancies for the
finance alert path. The worker never mutates financial records; it only reports
(see app.services.payments.reconciliation).
"""

from __future__ import annotations

from datetime import date, timedelta

from app.core.logging import get_logger
from app.services.payments.reconciliation import ReconciliationReport, reconcile

logger = get_logger(__name__)


async def run(previous_day: date | None = None) -> ReconciliationReport:
    """Reconcile one accounting day and surface any discrepancy count."""
    period = previous_day or (date.today() - timedelta(days=1))
    report = await reconcile(period)
    if report.discrepancies:
        logger.error(
            "reconciliation.discrepancies",
            period=period.isoformat(),
            count=len(report.discrepancies),
        )
    else:
        logger.info("reconciliation.clean", period=period.isoformat())
    return report
