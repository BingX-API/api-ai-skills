---
name: bingx-copytrade-swap
description: BingX Copy Trade USDT-M Perpetual Contracts — query trader's current orders, close positions, set take profit/stop loss, view trading overview and profit data, set commission rate, and get copy trading pairs. Use when the user asks about BingX copy trade perpetual swap orders, closing copy trade positions, setting TP/SL on copy trade orders, swap copy trade profit overview, commission rate for copy trading, or available copy trading pairs.
category: copy-trade
---

# BingX Copy Trade USDT-M Perpetual Contracts

Authenticated endpoints for BingX Copy Trade USDT-M (USDT-margined) perpetual futures. All endpoints require HMAC SHA256 signature authentication.

This skill covers the **trader (signal provider)** side of USDT-M perpetual futures copy trading: managing open orders, closing positions, setting TP/SL, querying performance data, configuring commission rate, and browsing available copy trading pairs.

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

> **Note:** Copy Trade USDT-M Perpetual Contracts endpoints are documented at `https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/`. Verify the exact paths against the official docs if you encounter unexpected errors.

---

## Quick Reference

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/openApi/copyTrading/v1/swap/trace/currentTrack` | GET | Trader's current (open) orders | Yes |
| `/openApi/copyTrading/v1/swap/trace/closeTrackOrder` | POST | Close position by order number | Yes |
| `/openApi/copyTrading/v1/swap/trace/setTPSL` | POST | Set take profit and stop loss by order number | Yes |
| `/openApi/copyTrading/v1/PFutures/traderDetail` | GET | Personal Trading Overview | Yes |
| `/openApi/copyTrading/v1/PFutures/profitHistorySummarys` | GET | Profit Overview | Yes |
| `/openApi/copyTrading/v1/PFutures/profitDetail` | GET | Profit Details (paginated) | Yes |
| `/openApi/copyTrading/v1/PFutures/setCommission` | POST | Set Commission Rate | Yes |
| `/openApi/copyTrading/v1/PFutures/tradingPairs` | GET | Trader Gets Copy Trading Pairs | Yes |

---

## Parameters

### Order Close Parameters

* **orderId**: The copy trade order number to close (required)
* **recvWindow**: Request validity window in milliseconds (optional, max 60000)

### TP/SL Parameters

* **orderId**: The copy trade order number to set TP/SL on (required)
* **takeProfit**: Take profit price as a string decimal (optional)
* **stopLoss**: Stop loss price as a string decimal (optional)
* **recvWindow**: Request validity window in milliseconds (optional, max 60000)

### Query Parameters (shared by overview, profit, and current orders endpoints)

* **symbol**: Trading pair filter in `BASE-USDT` format, e.g. `BTC-USDT` (optional)
* **startTime**: Start timestamp in **milliseconds** (optional)
* **endTime**: End timestamp in **milliseconds** (optional)
* **pageIndex**: Page number — must be greater than 0 (optional, default 1)
* **pageSize**: Number of records per page (optional, default varies by endpoint)
* **recvWindow**: Request validity window in milliseconds (optional)

### Commission Rate Parameters

* **commissionRate**: Commission rate value as a decimal string, e.g. `"0.001"` (required)

### Parameter Validation Rules

* **orderId**: Required for close/TP-SL operations; must be a valid order ID string
* **takeProfit** / **stopLoss**: When provided, must be a positive number (> 0) as a string decimal
* **symbol**: When provided, must match `^[A-Z0-9]+-USDT$` (e.g., `BTC-USDT`)
* **commissionRate**: Decimal string, must be ≥ 0 (e.g., `"0.001"`)
* **pageIndex**: Positive integer, must be > 0
* **pageSize**: Positive integer, must be > 0; varies per endpoint
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

**Query trader's current open orders:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/copyTrading/v1/swap/trace/currentTrack", {
    symbol: "BTC-USDT",
  }
);
// result.list — array of current open copy trade orders
// result.total — total count
```

**Close a position by order number:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/copyTrading/v1/swap/trace/closeTrackOrder", {
    orderId: "1736011869418901234",
  }
);
// result — confirmation of the close order
```

**Set take profit and stop loss:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/copyTrading/v1/swap/trace/setTPSL", {
    orderId: "1736011869418901234",
    takeProfit: "70000",
    stopLoss:   "60000",
  }
);
// result — confirmation that TP/SL was set
```

**Query personal trading overview:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/copyTrading/v1/PFutures/traderDetail"
);
// result.totalProfit, result.winRate, result.totalFollowers, etc.
```

**Query profit overview for a date range:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/copyTrading/v1/PFutures/profitHistorySummarys", {
    startTime: 1704067200000,
    endTime:   1706745600000,
  }
);
// result.netProfit, result.winRate, result.totalOrders, etc.
```

**Query profit details (paginated):**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/copyTrading/v1/PFutures/profitDetail", {
    startTime: 1704067200000,
    endTime:   1706745600000,
    pageIndex: 1,
    pageSize:  50,
  }
);
// result.list — per-order profit breakdown
// result.total — total count
```

**Set commission rate:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/copyTrading/v1/PFutures/setCommission", {
    commissionRate: "0.001",
  }
);
// result — confirmation of commission rate update
```

**Get copy trading pairs:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/copyTrading/v1/PFutures/tradingPairs"
);
// result.list — array of available copy trading pair objects
```

## Additional Resources

For full parameter descriptions and response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

Write operations (`closePosition`, `setTPSL`, `setCommissionRate`) require **CONFIRM** on `prod-live`. All GET endpoints are read-only and do not require confirmation.

- **prod-live**: Ask user to type **CONFIRM** before executing any write operation.
- **prod-vst**: No CONFIRM required. Inform user: "You are operating in the Production Simulated (VST) environment."

### Step 1 — Identify the Operation

If the user's intent is unclear, present options:

> What would you like to do?
> - View my current open copy trade orders
> - Close a position (by order number)
> - Set take profit / stop loss on an order
> - View my personal trading overview
> - View profit overview
> - View profit details
> - Set my commission rate
> - Get available copy trading pairs

### Step 2 — Collect Parameters

**For close position or set TP/SL:**
> Please provide the order ID:
> - orderId (required): the copy trade order number

**For set TP/SL additionally:**
> Please provide the TP/SL prices (at least one required):
> - takeProfit: take profit trigger price
> - stopLoss: stop loss trigger price

**For set commission rate:**
> Please provide the commission rate (e.g. `0.001` for 0.1%):
> - commissionRate (required)

**For profit/current orders queries:**
> Please specify a symbol and/or time range (optional):
> - Symbol (e.g. BTC-USDT)
> - Start time (Unix ms)
> - End time (Unix ms)

### Step 3 — Confirm (prod-live write ops only)

**Close position:**
> You are about to **close a copy trade position** on **Production Live**:
> - Order ID: `{orderId}`
>
> Type **CONFIRM** to proceed, or anything else to cancel.

**Set TP/SL:**
> You are about to **set TP/SL** on **Production Live**:
> - Order ID: `{orderId}`
> - Take Profit: `{takeProfit}`
> - Stop Loss: `{stopLoss}`
>
> Type **CONFIRM** to proceed, or anything else to cancel.

**Set Commission Rate:**
> You are about to **set your commission rate** to `{commissionRate}` on **Production Live**.
>
> Type **CONFIRM** to proceed, or anything else to cancel.

### Step 4 — Execute and Report

Execute the API call and return key fields to the user:
- For close position: order status and confirmation details
- For set TP/SL: confirmation of the new TP/SL values
- For set commission rate: confirmation of the new rate
- For trading overview: total profit, win rate, follower count, and AUM
- For profit overview: net profit, win rate, and total order count
- For profit details: per-order breakdown with symbol, profit, and timestamps
- For current orders: list of open orders with symbol, side, size, and entry price
- For copy trading pairs: list of available symbols for copy trading
