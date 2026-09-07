#!/usr/bin/env python3
"""Emit the command to replay a stored webhook event (runbook helper).

Backs ``docs/runbooks/webhook-replay.md``. Given a provider and an event id it
prints the exact, signature-aware ``curl`` invocation an operator uses to
re-deliver an event to the local endpoint. It never fabricates a signature: the
real signature must come from the provider (its dashboard, or the stored raw
payload plus the signing secret). Because handlers are idempotent on the event id
(ADR-005), a replay never double-applies a payment or a CRM change.

The idempotency ledger is not yet persisted, so this tool prints the procedure
and command template rather than reading a stored payload.

Usage::

    python scripts/replay_webhook.py stripe evt_1ABC
    python scripts/replay_webhook.py paysera 987 --base-url http://localhost:8000
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class _Provider:
    """Where a provider's webhook lives and how its signature is supplied."""

    name: str
    path: str
    signature_flag: str
    note: str


# Paths mirror the mounted routes (app/api/v1/webhooks/router.py) under the /v1
# prefix. argparse ``choices`` turns an unknown provider into a loud exit(2),
# never a silent no-op.
_PROVIDERS: dict[str, _Provider] = {
    "stripe": _Provider(
        name="stripe",
        path="/v1/webhooks/stripe",
        signature_flag='-H "Stripe-Signature: <resend from the Stripe dashboard>"',
        note=(
            "Stripe > Developers > Events > select the event > Resend, or replay the\n"
            "#     stored raw payload signed with STRIPE_WEBHOOK_SECRET."
        ),
    ),
    "paysera": _Provider(
        name="paysera",
        path="/v1/webhooks/paysera",
        signature_flag='--data-urlencode "ss2=<recomputed with the sign password>"',
        note=(
            "Paysera signs the ordered query parameters; recompute ss2 with\n"
            "#     PAYSERA_SIGN_PASSWORD and send it as ?ss2= or X-Paysera-Signature."
        ),
    ),
    "bitrix24": _Provider(
        name="bitrix24",
        path="/v1/webhooks/bitrix24",
        signature_flag='-H "X-Bitrix-Token: <integration token from the webhook URL>"',
        note=(
            "Bitrix24 authenticates with the integration token embedded in the\n"
            "#     webhook URL; supply it as X-Bitrix-Token (or ?token=)."
        ),
    ),
}


def replay_command(provider: _Provider, event_id: str, base_url: str) -> str:
    """Return the curl invocation that re-delivers ``event_id`` to the endpoint."""
    url = f"{base_url.rstrip('/')}{provider.path}"
    return "\n".join(
        [
            f'curl -sS -X POST "{url}" \\',
            '  -H "Content-Type: application/json" \\',
            f'  -H "Idempotency-Key: {event_id}" \\',
            f"  {provider.signature_flag} \\",
            "  --data @payload.json",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    """Entry point; returns a process exit code."""
    parser = argparse.ArgumentParser(description="Emit a webhook replay command.")
    parser.add_argument("provider", choices=sorted(_PROVIDERS), help="webhook provider")
    parser.add_argument("event_id", help="provider event id, reused as the idempotency key")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)",
    )
    args = parser.parse_args(argv)

    provider = _PROVIDERS[args.provider]
    print(f"# provider : {provider.name}")
    print(f"# event id : {args.event_id}")
    print(f"# target   : {args.base_url.rstrip('/')}{provider.path}")
    print("# Save the real payload to payload.json first; never invent a signature.\n")
    print(replay_command(provider, args.event_id, args.base_url))
    print(f"\n# How to obtain a valid signature:\n#     {provider.note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
