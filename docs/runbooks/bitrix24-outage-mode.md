# Runbook — Bitrix24 outage mode

> When the Bitrix24 EU instance is unreachable, the API enters a
> queue-and-sync fallback: CRM writes are buffered in Redis and flushed when
> connectivity returns. This runbook describes the behaviour and the operator
> actions required.

## How the circuit breaker works

The Bitrix24 adapter (`app/services/bitrix24/circuit_breaker.py`) tracks
consecutive failures. After a configurable threshold of failures within a
time window, the breaker opens:

| State | Behaviour |
| --- | --- |
| **Closed** (normal) | Every CRM call hits Bitrix24 in real time |
| **Open** (outage) | CRM writes are enqueued to Redis (`bitrix24:outbox`); reads return a `503` with `Retry-After` |
| **Half-open** | One probe call is allowed through; success closes the breaker, failure re-opens it |

The breaker is per-process and resets on restart. The Redis outbox survives
restarts.

## Detecting an outage

Symptoms:

- Structured logs show `bitrix24.circuit_breaker` transitioning to `open`.
- `/v1/health` reports `"bitrix24": "degraded"`.
- Bitrix24 dashboard (if accessible) confirms the EU instance is down.

## During the outage

1. **Confirm** the outage via the Bitrix24 status page or support channel.
2. **Monitor** the Redis outbox depth:
   ```bash
   redis-cli LLEN bitrix24:outbox
   ```
3. **Do not** disable the circuit breaker manually — the queue-and-sync path
   is safe and preserves ordering.
4. **Notify** affected tenants if CRM sync delay impacts their workflow
   (e.g. new donor records not visible in Bitrix24).

## After Bitrix24 recovers

1. The circuit breaker transitions to half-open automatically on the next
   probe call (default: 30 s after the last failure).
2. The background sync worker (`app/workers/bitrix24_sync_worker.py`) drains
   the outbox in FIFO order, replaying each buffered write.
3. Verify drain completion:
   ```bash
   redis-cli LLEN bitrix24:outbox   # should be 0
   ```
4. Check structured logs for `bitrix24.sync` entries with `status: drained`.
5. If any entries failed permanently (e.g. the CRM record was deleted while
   offline), they are moved to `bitrix24:dead-letter` — investigate manually.

## Data consistency notes

- All CRM writes are idempotent (ADR-005): the outbox entries carry the
  provider event id as the idempotency key, so a replay after recovery never
  creates duplicate contacts or deals.
- The outbox is bounded by Redis memory; under normal load the queue holds
  days of events. If the outage is expected to last > 24 h, consider
  increasing Redis memory or enabling the `BITRIX24_OUTAGE_MODE=reject`
  environment variable to return `503` immediately instead of buffering.

## Rollback

No code change is needed to exit outage mode. The circuit breaker closes
automatically when Bitrix24 responds successfully. If the outbox contains
stale entries after a prolonged outage, clear it manually:

```bash
redis-cli DEL bitrix24:outbox       # discard buffered writes
redis-cli DEL bitrix24:dead-letter  # discard unrecoverable entries
```

**Warning:** discarding the outbox means those CRM writes are lost. Only do
this when the buffered data is confirmed stale or duplicate.
