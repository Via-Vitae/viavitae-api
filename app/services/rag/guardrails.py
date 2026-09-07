"""Input and output guardrails for the pastoral assistant (ADR-007).

These are the deterministic first-line screens. The safety-critical case -- a
person in crisis -- fails CLOSED: it is blocked and signed off to a named human
resource rather than answered by the model. Richer classifiers (doctrine,
prompt-injection, personal-data detection) are stubbed as TODO and layer on top
of this screen without ever relaxing it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

# A deliberately small, high-precision multilingual crisis lexicon (EN/LT/RU).
# It favours blocking -- a false positive routes to a human, which is safe --
# over missing a genuine crisis. Extend per locale as the classifier matures.
_CRISIS_TERMS = frozenset(
    {
        "kill myself",
        "killing myself",
        "end my life",
        "take my own life",
        "suicide",
        "suicidal",
        "self-harm",
        "self harm",
        "hurt myself",
        "savižudybė",
        "savižudis",
        "žudytis",
        "nusižudyti",
        "žaloju save",
        "суицид",
        "самоубийство",
        "убить себя",
        "порезать себя",
    }
)

CRISIS_SIGNPOST = (
    "This message was not answered automatically. If you or someone else is in "
    "immediate danger, contact your pastor or the Lithuanian emotional support "
    "line 1809 (24/7). The request has been routed to a named human responder."
)


class GuardrailVerdict(StrEnum):
    """Outcome of a guardrail evaluation."""

    ALLOW = "allow"
    MODIFY = "modify"
    BLOCK = "block"


class BlockReason(StrEnum):
    """Why a request or draft was blocked."""

    OUT_OF_SCOPE = "out_of_scope"
    DOCTRINAL_DISPUTE = "doctrinal_dispute"
    PASTORAL_CRISIS = "pastoral_crisis"
    PERSONAL_DATA = "personal_data"
    SACRAMENTAL_RECORD = "sacramental_record"
    FINANCIAL_ADVICE = "financial_advice"
    MEDICAL_ADVICE = "medical_advice"
    PROMPT_INJECTION = "prompt_injection"


@dataclass(slots=True, frozen=True)
class GuardrailResult:
    """A verdict with a human-readable explanation for the approver."""

    verdict: GuardrailVerdict
    reasons: tuple[BlockReason, ...] = ()
    note: str = ""

    @property
    def blocked(self) -> bool:
        """True when generation or publication must not proceed."""
        return self.verdict is GuardrailVerdict.BLOCK


def _crisis_screen(text: str) -> tuple[BlockReason, ...]:
    """Return the crisis reason when the text matches the lexicon, else empty."""
    lowered = text.lower()
    if any(term in lowered for term in _CRISIS_TERMS):
        return (BlockReason.PASTORAL_CRISIS,)
    return ()


async def check_input(text: str, *, locale: str) -> GuardrailResult:
    """Screen the user request before retrieval and generation.

    Crisis handling is explicit: mentions of self-harm are blocked and signed
    off to a named human -- never answered by the model.
    """
    reasons = _crisis_screen(text)
    if reasons:
        return GuardrailResult(GuardrailVerdict.BLOCK, reasons, CRISIS_SIGNPOST)
    # TODO(api): add out-of-scope, prompt-injection and personal-data screens,
    #            locale-aware (``locale``), plus an embedding classifier.
    _ = locale
    return GuardrailResult(verdict=GuardrailVerdict.ALLOW)


async def check_output(draft: str, *, locale: str) -> GuardrailResult:
    """Screen the generated draft before it reaches the approval queue."""
    reasons = _crisis_screen(draft)
    if reasons:
        return GuardrailResult(GuardrailVerdict.BLOCK, reasons, CRISIS_SIGNPOST)
    # TODO(api): enforce a citation-coverage floor and banned-inference checks.
    _ = locale
    return GuardrailResult(verdict=GuardrailVerdict.ALLOW)
