"""Paysera adapter: project payments, callback signature verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True, frozen=True)
class ChargeResult:
    """Provider-neutral outcome of a payment attempt."""

    provider_reference: str
    status: str  # created | succeeded | failed | refunded
    amount_minor: int
    currency: str
    raw_status: str


class PaymentAdapter(Protocol):
    """Contract every payment provider adapter implements.

    Rationale: `viavitae-web`, the donation flow and reconciliation must not
    depend on a single PSP. Adapters are swap-in/swap-out.
    """

    async def create_checkout(
        self, *, amount_minor: int, currency: str, tenant_id: str, reference: str, return_url: str
    ) -> str: ...

    async def fetch_charge(self, provider_reference: str) -> ChargeResult: ...

    async def refund(
        self, provider_reference: str, *, amount_minor: int | None = None
    ) -> ChargeResult: ...

    async def verify_signature(self, payload: bytes, signature: str) -> bool: ...


# TODO(api): implement the concrete adapter for this provider against the
# contract above, using EU-region endpoints only, and cover it with contract
# tests in tests/contract/.
