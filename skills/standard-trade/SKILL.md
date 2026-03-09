---
name: bingx-standard-trade
description: Query BingX standard contract positions, historical orders, and account balance. Use when the user asks about BingX standard contract positions, standard futures order history, or standard contract balance.
---

# BingX Standard Contract Trading

Authenticated endpoints for BingX standard contract (standard futures) data. All endpoints require HMAC SHA256 signature authentication.

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

---

## Quick Reference

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/openApi/contract/v1/allPosition` | GET | Query current positions | Yes |
| `/openApi/contract/v1/allOrders` | GET | Query historical orders | Yes |
| `/openApi/contract/v1/balance` | GET | Query standard contract balance | Yes |

---

## 1. Query Positions

`GET /openApi/contract/v1/allPosition`

Query all current positions in the standard contract account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|

**Response `data` (array):**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair, e.g. BTC-USDT |
| `initialMargin` | number | Margin |
| `leverage` | number | Leverage |
| `unrealizedProfit` | number | Unrealized profit and loss |
| `isolated` | bool | `true` = isolated margin mode |
| `entryPrice` | number | Average entry price |
| `positionSide` | string | Position direction: `LONG` or `SHORT` |
| `positionAmt` | number | Position quantity |
| `currentPrice` | number | Current price |
| `time` | int64 | Opening time (ms) |

---

## 2. Query Historical Orders

`GET /openApi/contract/v1/allOrders`

Query historical orders for a standard contract trading pair.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. BTC-USDT |
| `orderId` | int64 | No | Order ID filter |
| `startTime` | int64 | No | Start time in milliseconds |
| `endTime` | int64 | No | End time in milliseconds |
| `limit` | int64 | No | quantity, optional |
| `recvWindow` | int64 | No | Request validity window (milliseconds) |

**Response `data` (array):**

| Field | Type | Description |
|-------|------|-------------|
| `orderId` | number | System order ID |
| `symbol` | string | Trading pair |
| `positionSide` | string | Position direction: `LONG` or `SHORT` |
| `status` | string | Order status, e.g. `CLOSED` |
| `avgPrice` | number | Average fill price |
| `cumQuote` | number | Transaction amount |
| `executedQty` | number | Filled quantity |
| `margin` | number | Margin |
| `leverage` | number | Leverage |
| `isolated` | bool | `true` = isolated margin mode |
| `closePrice` | number | Closing price |
| `positionId` | int64 | Position ID |
| `time` | int64 | Order time (ms) |
| `updateTime` | int64 | Last update time (ms) |

---

## 3. Query Standard Contract Balance

`GET /openApi/contract/v1/balance`

Query the standard contract account balance.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `asset` | string | Asset name |
| `balance` | string | Total balance |
| `crossWalletBalance` | string | Cross-margin wallet balance |
| `crossUnPnl` | string | Cross-margin unrealized PnL |
| `availableBalance` | string | Available balance for orders |
| `maxWithdrawAmount` | string | Maximum transferable amount |
| `marginAvailable` | bool | Whether it can be used as margin |
| `updateTime` | number | Last update timestamp |

### Parameter Validation Rules

* **symbol**: Must match `^[A-Z0-9]+-[A-Z]+$`; max 20 characters (e.g., `BTC-USDT`)
* **orderId**: When provided, must be a positive integer
* **startTime** / **endTime**: Unix timestamps in milliseconds; `endTime` must be ≥ `startTime`
* **limit**: Positive integer
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

**Query all positions:**

```typescript
const positions = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/contract/v1/allPosition"
);
// positions[].symbol, positions[].positionAmt, positions[].unrealizedProfit, positions[].entryPrice
```

**Query historical orders for BTC-USDT:**

```typescript
const orders = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/contract/v1/allOrders", { symbol: "BTC-USDT", limit: 50 }
);
// orders[].orderId, orders[].status, orders[].avgPrice, orders[].executedQty
```

**Query account balance:**

```typescript
const balance = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/contract/v1/balance"
);
// balance.balance, balance.availableBalance, balance.crossUnPnl
```

## Additional Resources

For complete parameter descriptions and full response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

All standard-trade endpoints are **read-only** (GET). No CONFIRM required — they never modify account state.

Credentials are required. If no account is specified, default to the `main` account.

### Step 1 — Identify the query

If the user's intent is unclear, present options:

> Please select the information type to query:
> - Current positions / Unrealized PnL — positions
> - Historical orders — allOrders
> - Account balance / Available margin — balance

### Step 2 — Collect parameters

For `allOrders`, `symbol` is required. If the user asks about a specific coin, infer the symbol (e.g., "BTC orders" -> `BTC-USDT`). Optional filters include `startTime`, `endTime`, and `limit`.

For `allPosition` and `balance`, no parameters are needed.

### Step 3 — Execute and report

Execute the API call and present results in a readable format:

- **positions**: Show a table per position: symbol, side, amount, entry price, unrealized PnL, leverage.
- **allOrders**: Show a table: order ID, symbol, side, status, average fill price, quantity, time.
- **balance**: Show total balance, available balance, cross unrealized PnL.
