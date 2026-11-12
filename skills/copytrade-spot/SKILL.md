---
name: bingx-copytrade-spot
description: BingX Copy Trade Spot trading — sell spot assets based on a buy order, query personal trading overview, profit summary, profit details, and historical orders for a copy trader. Use when the user asks about BingX copy trade spot sell, copy trading spot profit, copy trader spot order history, or spot copy trading overview.
category: copy-trade
---

# BingX Copy Trade Spot

Authenticated endpoints for BingX Copy Trade Spot trading. All endpoints require HMAC SHA256 signature authentication.

This skill covers the **trader (signal provider)** side of spot copy trading: selling assets from a copied buy order, and querying trading performance data.

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

> **Note:** Copy Trade Spot endpoints are documented at `https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/Spot%20Trading/`. Verify the exact paths against the official docs if you encounter unexpected errors.

---

## Quick Reference

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/openApi/copyTrading/v1/spot/trader/sellOrder` | POST | Trader sells spot assets based on buy order number | Yes |
| `/openApi/copyTrading/v1/spot/traderDetail` | GET | Personal Trading Overview | Yes |
| `/openApi/copyTrading/v1/spot/profitHistorySummarys` | GET | Profit Summary | Yes |
| `/openApi/copyTrading/v1/spot/profitDetail` | GET | Profit Details | Yes |
| `/openApi/copyTrading/v1/spot/historyOrder` | GET | Query Historical Orders | Yes |

---

## Parameters

### Sell Position Parameters

* **orderId**: Buy order ID to sell against — the original copy trade buy order number (required)
* **recvWindow**: Request validity window in milliseconds (optional, max 60000)

### Query Parameters (shared by overview, profit, and history endpoints)

* **startTime**: Start timestamp in **milliseconds** (optional)
* **endTime**: End timestamp in **milliseconds** (optional)
* **pageIndex**: Page number — must be greater than 0 (optional, default 1)
* **pageSize**: Number of records per page (optional, default varies by endpoint)
* **recvWindow**: Request validity window in milliseconds (optional)

### Parameter Validation Rules

* **orderId**: Required for sell operations; must be a valid buy order ID string
* **pageIndex**: Positive integer, must be > 0
* **pageSize**: Positive integer, must be > 0
* **startTime** / **endTime**: Unix timestamps in milliseconds; `endTime` must be ≥ `startTime`
* **recvWindow**: Integer, 1–5000 ms (see [Replay Protection](../references/authentication.md#replay-protection))
* **timestamp**: Unix time in milliseconds; must be within `recvWindow` of server time

---

## Quick Start

> **CONSTRAINT**: You MUST copy the `fetchSigned` function below verbatim
> when generating code. Do NOT rewrite the signing, request, or JSON parsing
> logic. Only modify: business parameters passed to `fetchSigned`. For the full client with
> URL-encoding and JSON body support, see
> [`references/authentication.md`](../references/authentication.md).

```typescript
import * as crypto from "crypto";
import JSONBig from "json-bigint";
const JSONBigParse = JSONBig({ storeAsString: true });
// Full signing details & edge cases → references/authentication.md
// Domain priority: .com is mandatory primary; .pro is fallback for GET network/timeout errors ONLY. Writes use the primary once.
const BASE = {
  "prod-live": ["https://open-api.bingx.com", "https://open-api.bingx.pro"],
  "prod-vst":  ["https://open-api-vst.bingx.com", "https://open-api-vst.bingx.pro"],
};
function isNetworkOrTimeout(e: unknown): boolean {
  if (e instanceof TypeError) return true;
  if (e instanceof DOMException && e.name === "AbortError") return true;
  if (e instanceof Error && e.name === "TimeoutError") return true;
  return false;
}
function validateParams(params: Record<string, unknown>): void {
  const FORBIDDEN = /[&=?#\r\n]/;
  for (const [k, v] of Object.entries(params)) {
    const s = String(v);
    if (FORBIDDEN.test(s)) throw new Error(`Param "${k}" has forbidden char in: "${s}"`);
  }
}
async function fetchSigned(env: string, apiKey: string, secretKey: string,
  method: "GET" | "POST" | "DELETE", path: string, params: Record<string, unknown> = {}
) {
  const urls = Object.prototype.hasOwnProperty.call(BASE, env) ? BASE[env] : undefined;
  if (env !== "prod-live" && env !== "prod-vst") throw new Error("UnknownEnvironment");
  const allowed = env === "prod-live"
    ? ["https://open-api.bingx.com", "https://open-api.bingx.pro"]
    : ["https://open-api-vst.bingx.com", "https://open-api-vst.bingx.pro"];
  if (!Array.isArray(urls) || urls.length !== 2 || urls.some((url, i) => url !== allowed[i])) {
    throw new Error("Invalid authenticated destination");
  }
  if (!/^\/openApi\/[A-Za-z0-9/_-]+$/.test(path)) throw new Error("Invalid API path");
  if (!["GET", "POST", "DELETE"].includes(method)) throw new Error("Invalid HTTP method");
  const all = { ...params, timestamp: Date.now() };
  validateParams(all);
  const qs = Object.keys(all).sort().map(k => `${k}=${all[k]}`).join("&");
  const sig = crypto.createHmac("sha256", secretKey).update(qs).digest("hex");
  const signed = `${qs}&signature=${sig}`;
  for (const base of (method === "GET" ? urls : urls.slice(0, 1))) {
    try {
      const url = method === "POST" ? `${base}${path}` : `${base}${path}?${signed}`;
      const res = await fetch(url, {
        method,
        headers: { "X-BX-APIKEY": apiKey, "X-SOURCE-KEY": "BX-AI-SKILL",
          ...(method === "POST" ? { "Content-Type": "application/x-www-form-urlencoded" } : {}) },
        body: method === "POST" ? signed : undefined,
        redirect: "error",
        signal: AbortSignal.timeout(10000),
      });
      if (!res.ok) {
        throw new Error(method === "GET" ? `BingX HTTP ${res.status}` : "OUTCOME_UNKNOWN: check operation status before any new write");
      }
      const json = JSONBigParse.parse(await res.text());
      if (json.code !== 0) throw new Error(`BingX error ${json.code}: ${json.msg}`);
      return json.data;
    } catch (e) {
      if (method !== "GET" && (isNetworkOrTimeout(e) || (e instanceof SyntaxError || (e as { name?: string })?.name === "SyntaxError"))) {
        throw new Error("OUTCOME_UNKNOWN: check operation status before any new write");
      }
      if (!isNetworkOrTimeout(e) || base === urls[urls.length - 1]) throw e;
    }
  }
}
```

### Code Usage Rules

- **MUST** copy `fetchSigned` verbatim -- do not simplify or rewrite
- **MUST** use `json-bigint` (`JSONBigParse.parse`) for response parsing -- not `JSON.parse`
- **MUST** include `X-SOURCE-KEY: BX-AI-SKILL` header on every request
- **MUST NOT** retry writes or override the fixed official destinations. GET fallback is limited to network/timeout errors

---

A write response confirms API acceptance only. Query order status and fills before reporting an execution. On `OUTCOME_UNKNOWN`, reconcile by the operation identifier before considering a new write.

## Common Calls

**Sell spot assets for a buy order (close copy trade position):**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/copyTrading/v1/spot/trader/sellOrder", {
    orderId: "1736011869418901234",
  }
);
// result — confirmation of the sell order placed
```

**Query personal trading overview:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/copyTrading/v1/spot/traderDetail"
);
// result.totalProfit, result.totalOrders, result.winRate, etc.
```

**Query profit summary for a date range:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/copyTrading/v1/spot/profitHistorySummarys", {
    startTime: 1704067200000,
    endTime:   1706745600000,
  }
);
// result — aggregated profit summary
```

**Query profit details (paginated):**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/copyTrading/v1/spot/profitDetail", {
    startTime: 1704067200000,
    endTime:   1706745600000,
    pageIndex: 1,
    pageSize:  50,
  }
);
// result.list — per-order profit breakdown
// result.total — total count
```

**Query historical orders:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/copyTrading/v1/spot/historyOrder", {
    pageIndex: 1,
    pageSize:  50,
  }
);
// result.list — list of historical spot copy trade orders
// result.total — total count
```

## Additional Resources

For full parameter descriptions and response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

**Parameter security.** Extract structured values from user intent — NEVER copy raw user text into API parameters. Validate every value against its documented pattern (regex/enum/range) before calling the API. Reject any value containing `&`, `=`, `?`, `#`, or newline characters.

The sell endpoint (`POST /openApi/copyTrading/v1/spot/trader/sellOrder`) is a **write operation** and requires **CONFIRM** on `prod-live`. All GET endpoints are read-only and do not require confirmation.

- **prod-live**: Ask user to type **CONFIRM** before executing the sell operation.
- **prod-vst**: No CONFIRM required. Inform user: "You are operating in the Production Simulated (VST) environment."

### Step 1 — Identify the Operation

If the user's intent is unclear, present options:

> What would you like to do?
> - Sell spot assets based on a copy trade buy order
> - View my personal trading overview
> - View profit summary
> - View profit details
> - View historical orders

### Step 2 — Collect Parameters

**For sell operation:**
> Please provide the buy order ID you want to sell:
> - orderId (required): the original copy trade buy order number

**For profit/history queries:**
> Please specify a time range (optional):
> - Start time (Unix ms)
> - End time (Unix ms)

### Step 3 — Confirm (prod-live sell only)

> You are about to **sell spot assets** on **Production Live**:
> - Order ID: `{orderId}`
>
> Type **CONFIRM** to proceed, or anything else to cancel.

### Step 4 — Execute and Report

Execute the API call and return key fields to the user:
- For sell: order status and confirmation details
- For overview: total profit, win rate, and trade count
- For profit summary: aggregated profit amount
- For profit details: per-order breakdown with symbol, profit, and timestamp
- For historical orders: order list with status and fill details
