# BingX API Rate Limits — Global Reference

This document is the single source of truth for **rate limiting policy** across all BingX OpenAPI endpoints. Each `api-reference.md` file annotates per-endpoint limits inline (e.g. `Rate limit: 5/s per UID; 2/s per IP.`) — this file explains the dimensions, error semantics, and recommended client-side behavior.

---

## 1. Dimensions

BingX enforces rate limits on **two independent dimensions**. Either dimension being exceeded triggers `100410`.

| Dimension | Scope | Typical range | When it applies |
|-----------|-------|---------------|-----------------|
| **Per-UID** | Per authenticated account (API key owner) | `1/s` – `30/s` | Authenticated REST + WebSocket login/subscribe requests |
| **Per-IP** | Per source IP address | `1/s` – `3/s` | All requests reaching the gateway, regardless of auth |

> An endpoint may have only one dimension (e.g. public market endpoints typically only have **per-IP** limits; copytrade endpoints often only have **per-UID** limits).

### Annotation format used in this repo

```
Rate limit: <UID-rate> per UID; <IP-rate> per IP.
Rate limit: <IP-rate> per IP.            # public market endpoints
Rate limit: <UID-rate> per UID.          # account-only-throttled endpoints
```

Examples actually used:

- `Rate limit: 10/s per UID; 3/s per IP.` — `POST /openApi/swap/v2/trade/order`
- `Rate limit: 1/s per IP.` — `GET /openApi/spot/v1/common/symbols`
- `Rate limit: 10/s per UID.` — `GET /openApi/copyTrading/v1/spot/profitDetail`

---

## 2. Order of precedence

When designing a client-side limiter, enforce in this order:

1. **Per-IP cap** at the egress (since one IP often serves many UIDs in a fleet).
2. **Per-UID cap** at the API-key level.
3. **Endpoint-specific cap** (read from each `api-reference.md`).

The effective ceiling for any single call is `min(IP_cap, UID_cap, endpoint_cap)`.

---

## 3. Error semantics — code `100410`

When any limit is exceeded, the gateway returns:

```json
{ "code": 100410, "msg": "Request rate limit exceeded...", "data": null }
```

See [`error-codes.md`](./error-codes.md) for full code list. Notes:

- `100410` is **transient**: it is safe to retry after backoff.
- The response does **not** carry a `Retry-After` header. Clients must implement their own backoff.
- Repeatedly hitting `100410` may escalate to **temporary IP/UID ban** (typically minutes to tens of minutes). Treat sustained `100410` as a bug, not a normal flow.
- `100421` (request rejected for business reasons such as too many open orders) is **not** the same as `100410` and must not be retried with backoff alone.

---

## 4. Client-side strategy — recommended

### 4.1 Token-bucket limiter (proactive)

Configure two independent buckets per process (or per IP+UID pair):

| Bucket | Capacity | Refill rate |
|--------|----------|-------------|
| IP bucket | `IP_cap` (peak burst) | `IP_cap / s` |
| UID bucket | `UID_cap` | `UID_cap / s` |

Each request must consume one token from **both** buckets. Block until both have a token. This avoids ever hitting `100410` on the happy path.

### 4.2 Exponential backoff with jitter (reactive — when 100410 is observed)

```
attempt = 0
while True:
    resp = call()
    if resp.code != 100410:
        return resp
    attempt += 1
    if attempt > MAX_RETRY:        # e.g. MAX_RETRY = 5
        raise RateLimitedError
    base   = min(2 ** attempt * 100, 5000)   # ms, capped at 5s
    jitter = random.randint(0, base // 2)    # full-jitter variant
    sleep(base + jitter)
```

Recommended defaults:

- `MAX_RETRY = 5` (≈ 5s + jitter total worst case)
- **Full jitter** (not equal jitter) to avoid thundering-herd retries from a fleet
- Reset `attempt` on the first non-`100410` response

### 4.3 Circuit breaker (defensive)

If `100410` ratio over a 30-second window exceeds **20%**, open the circuit for **60s** to let the gateway cool down. This protects both your service and avoids escalation to a temporary ban.

---

## 5. WebSocket-specific notes

- **Listen Key endpoints** (`/openApi/user/auth/userDataStream` POST/PUT/DELETE) are limited to `2/s per UID; 2/s per IP`. Refresh listen keys at most once every 30 minutes (validity is 60 minutes).
- **Subscription / login frames** on the WS connection itself are limited to `2/s per UID` for account streams. Public market WS subscriptions have per-connection rather than per-second caps — see each `*-ws-market` skill for `dataType` channel limits.
- Connection-level limits (max concurrent connections per UID/IP) are enforced separately by the gateway and are **not** counted toward `100410`. Excess connections are rejected at WebSocket handshake.

---

## 6. Capacity planning quick table

| Use case | Bottleneck | Recommended setup |
|----------|-----------|-------------------|
| Single retail bot, 1 UID | UID cap dominates | One token-bucket per endpoint, sized to endpoint cap |
| Market-making, 1 UID, multi-region | IP cap dominates per region | Distribute across IPs; each region uses its own IP bucket |
| Multi-tenant aggregator, N UIDs share 1 egress IP | IP cap dominates globally | Central IP-bucket gate **before** per-UID UID-bucket gates |
| Pure market-data scraper (no auth) | IP cap only | Rotate IPs; never share an IP with order endpoints |

---

## 7. Per-endpoint discovery

Every `skills/*/api-reference.md` annotates each endpoint with its inline `Rate limit:` line. The lint rule **"十一、Rate limit 标注完整性"** in `scripts/validate-skill-quality.py` enforces that every ``METHOD /openApi/...`` reference is followed (within 4 lines) by a `Rate limit:` line. Missing annotations are P0 (block push).

To search for a specific endpoint's limit:

```bash
grep -nE '`(GET|POST|PUT|DELETE) /openApi/swap/v2/trade/order`' skills/swap-trade/api-reference.md -A 4
```

---

## 8. Source of truth

Per-endpoint values in this repo are derived from the official internal documentation `bon-api/bingx-api-docs@feature/martin-dev`, fields `api.rate-limitation` (UID dimension) and `api.ip-rate-limitation` (IP dimension). Re-sync via the script under `scripts/` (or open an MR) when the upstream docs change.
