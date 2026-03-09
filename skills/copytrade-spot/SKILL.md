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

```typescript
import * as crypto from "crypto";
// Full signing details & edge cases → references/authentication.md
const BASE = {
  "prod-live": ["https://open-api.bingx.com", "https://open-api.bingx.pro"],
  "prod-vst":  ["https://open-api-vst.bingx.com", "https://open-api-vst.bingx.pro"],
};
async function fetchSigned(env: string, apiKey: string, secretKey: string,
  method: "GET" | "POST" | "DELETE", path: string, params: Record<string, unknown> = {}
) {
  const urls = BASE[env] ?? BASE["prod-live"];
  const all = { ...params, timestamp: Date.now() };
  const qs = Object.keys(all).sort().map(k => `${k}=${all[k]}`).join("&");
  const sig = crypto.createHmac("sha256", secretKey).update(qs).digest("hex");
  const signed = `${qs}&signature=${sig}`;
  for (const base of urls) {
    try {
      const url = method === "POST" ? `${base}${path}` : `${base}${path}?${signed}`;
      const res = await fetch(url, {
        method,
        headers: { "X-BX-APIKEY": apiKey, "X-SOURCE-KEY": "BX-AI-SKILL",
          ...(method === "POST" ? { "Content-Type": "application/x-www-form-urlencoded" } : {}) },
        body: method === "POST" ? signed : undefined,
      });
      const json = await res.json();
      if (json.code !== 0) throw new Error(`BingX error ${json.code}: ${json.msg}`);
      return json.data;
    } catch (e) {
      if (base === urls[urls.length - 1]) throw e;
    }
  }
}
```

---

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
