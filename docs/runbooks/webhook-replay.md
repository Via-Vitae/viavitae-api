# Runbook — Webhook replay

> Backs `scripts/replay_webhook.py`. All webhook handlers are idempotent on the
> provider event id (ADR-005), so a replay never double-applies a payment or a
> CRM change.

## When to use

- A webhook was received but the handler returned a 5xx (transient failure).
- The provider dashboard shows an event as "failed" or "pending delivery".
- An operator needs to re-process a specific event after a deployment fix.

## Prerequisites

| Item | Source |
| --- | --- |
| Provider event id | Stripe Dashboard → Developers → Events, or Paysera/Bitrix24 logs |
| Raw payload | Provider dashboard "Resend", or application structured log (`payload_hash`) |
| Valid signature | Must come from the provider — never fabricate one |
| `DATABASE_URL` | Control-plane or runtime DSN with access to the idempotency ledger |

## Steps

### 1. Save the payload

Download the raw JSON payload from the provider dashboard and save it to
`payload.json`. Do **not** reconstruct it manually — the signature is bound to
the exact byte sequence.

```bash
# Example: copy from Stripe Dashboard → Developers → Events → <event> → Resend
```

### 2. Generate the replay command

```bash
python scripts/replay_webhook.py stripe evt_1ABCdef234
python scripts/replay_webhook.py paysera 987 --base-url https://api.viavitae.eu
python scripts/replay_webhook.py bitrix24 BX-xyz --base-url http://localhost:8000
```

The script prints a `curl` invocation with the correct endpoint, signature
header position, and the event id as the `Idempotency-Key`.

### 3. Obtain a valid signature

| Provider | How |
| --- | --- |
| Stripe | Use the Stripe dashboard "Resend" button (re-signs automatically), or sign the stored payload with `STRIPE_WEBHOOK_SECRET` |
| Paysera | Recompute `ss2` from the ordered query parameters using `PAYSERA_SIGN_PASSWORD` |
| Bitrix24 | Supply the integration token from the webhook URL as `X-Bitrix-Token` |

### 4. Execute and verify

Run the printed `curl` command. Expected responses:

| Status | Meaning |
| --- | --- |
| `200` + `Idempotent-Replayed: true` | Event was already processed; stored result returned |
| `200` / `201` | Event processed for the first time |
| `409` | Idempotency key reused with a different payload — **investigate** |
| `401` / `403` | Invalid or missing signature — check step 3 |

## Safety notes

- The script **never** fabricates a signature. A real signature from the
  provider is required — this is fail-closed by design (ADR-005).
- Because handlers are idempotent, running the same replay twice is safe: the
  second run returns the stored result.
- If the idempotency ledger entry has expired (30-day TTL), the event is
  re-processed from scratch. Verify that money-moving side effects (receipts,
  CRM contacts) are themselves idempotent at the provider.
