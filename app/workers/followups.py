"""Follow-up sequences after an assessment submission (D+2, D+5, D+10)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import IntEnum


class FollowUpStep(IntEnum):
    """Days after submission for each follow-up message."""

    FIRST = 2
    SECOND = 5
    THIRD = 10


@dataclass(slots=True, frozen=True)
class FollowUp:
    """One scheduled follow-up message."""

    assessment_id: str
    step: FollowUpStep
    due_date: date
    locale: str
    sent: bool = False


def plan(submitted_on: date, assessment_id: str, locale: str) -> list[FollowUp]:
    """Build the follow-up schedule for a submission."""
    return [
        FollowUp(
            assessment_id=assessment_id,
            step=step,
            due_date=submitted_on + timedelta(days=int(step)),
            locale=locale,
        )
        for step in FollowUpStep
    ]


async def run_due(today: date) -> int:
    """Send every follow-up due today.

    Data-protection constraints (DPIA-001, measure M2):
      * at most one message per step, three steps in total, then stop;
      * an objection or unsubscribe cancels the remaining steps permanently;
      * no re-marketing after the sequence ends;
      * every send is logged with the assessment id, never the contact details.
    """
    # TODO(api): load due follow-ups, render locale templates, dispatch via
    #            app.services.notifications, record delivery.
    _ = today
    return 0
