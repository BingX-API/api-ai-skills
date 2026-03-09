---
name: bingx-spot-trade
description: BingX spot trading — place/cancel orders, query orders, view trade fills, manage OCO orders, and check commission rates. Use when the user asks about BingX spot order placement, cancellation, open orders, order history, transaction details, OCO orders, or spot trading commission rates.
---

# BingX Spot Trade

Authenticated trading endpoints for BingX spot market. All endpoints require HMAC SHA256 signature authentication.

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

---

## Quick Reference

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/openApi/spot/v1/trade/order` | POST | Place a single order | Yes |
| `/openApi/spot/v1/trade/batchOrders` | POST | Place multiple orders (max 5) | Yes |
| `/openApi/spot/v1/trade/cancel` | POST | Cancel an order | Yes |
| `/openApi/spot/v1/trade/cancelOrders` | POST | Cancel multiple orders | Yes |
| `/openApi/spot/v1/trade/cancelOpenOrders` | POST | Cancel all open orders on a symbol | Yes |
| `/openApi/spot/v1/trade/cancelAllAfter` | POST | Auto-cancel countdown (kill switch) | Yes |
| `/openApi/spot/v1/trade/order/cancelReplace` | POST | Cancel and replace order | Yes |
| `/openApi/spot/v1/trade/query` | GET | Query order details | Yes |
| `/openApi/spot/v1/trade/openOrders` | GET | Query current open orders | Yes |
| `/openApi/spot/v1/trade/historyOrders` | GET | Query order history | Yes |
| `/openApi/spot/v1/trade/myTrades` | GET | Query transaction details (trade fills) | Yes |
| `/openApi/spot/v1/user/commissionRate` | GET | Query trading commission rate | Yes |
| `/openApi/spot/v1/oco/order` | POST | Create OCO order | Yes |
| `/openApi/spot/v1/oco/cancel` | POST | Cancel OCO order | Yes |
| `/openApi/spot/v1/oco/orderList` | GET | Query OCO order list | Yes |
| `/openApi/spot/v1/oco/openOrderList` | GET | Query all open OCO orders | Yes |
| `/openApi/spot/v1/oco/historyOrderList` | GET | Query OCO historical order list | Yes |

---

## Parameters

### Order Parameters

* **symbol**: Trading pair in `BASE-QUOTE` format (e.g., `BTC-USDT`, `ETH-USDT`)
* **side**: Order direction — `BUY` or `SELL`
* **type**: Order type (see Enums)
* **quantity**: Order quantity in base asset (e.g., `0.1` BTC for BTC-USDT)
* **quoteOrderQty**: Order amount in quote asset (e.g., `100` USDT); `quantity` takes priority if both provided
* **price**: Limit price (required for `LIMIT`, `TAKE_STOP_LIMIT`, `TRIGGER_LIMIT`)
* **stopPrice**: Trigger price (required for `TAKE_STOP_LIMIT`, `TAKE_STOP_MARKET`, `TRIGGER_LIMIT`, `TRIGGER_MARKET`)
* **timeInForce**: `GTC` | `IOC` | `FOK` | `PostOnly` — default `GTC`; required for `LIMIT` type
* **newClientOrderId**: Custom order ID, 1–40 chars
* **recvWindow**: Request validity window in milliseconds (max 60000)
* **orderId**: System order ID (for cancel/query)
* **clientOrderID**: Custom order ID (for cancel/query)

### Enums

**type** (Order type):
- `MARKET` — Market order (fills immediately at best available price)
- `LIMIT` — Limit order (requires `price` and `timeInForce`)
- `TAKE_STOP_LIMIT` — Take-profit/stop-loss limit order (requires `stopPrice` and `price`)
- `TAKE_STOP_MARKET` — Take-profit/stop-loss market order (requires `stopPrice`)
- `TRIGGER_LIMIT` — Trigger limit order (requires `stopPrice` and `price`)
- `TRIGGER_MARKET` — Trigger market order (requires `stopPrice`)

**side**: `BUY` | `SELL`

**timeInForce**: `GTC` | `IOC` | `FOK` | `PostOnly`

**cancelReplaceMode**:
- `STOP_ON_FAILURE` — Abort if the cancel step fails
- `ALLOW_FAILURE` — Place the new order even if cancel fails

**cancelRestrictions** (limit cancellation by order status):
- `NEW` | `PENDING` | `PARTIALLY_FILLED`

### Parameter Validation Rules

Before sending a request, validate parameters client-side to avoid unnecessary API errors:

* **symbol**: Must match `^[A-Z0-9]+-[A-Z]+$`; max 20 characters (e.g., `BTC-USDT`)
* **quantity**: Must be a positive number (> 0); precision depends on the symbol's lot-size filter
* **quoteOrderQty**: When provided, must be a positive number (> 0); represents amount in quote asset
* **price**: When provided, must be a positive number (> 0)
* **stopPrice**: When provided, must be a positive number (> 0)
* **newClientOrderId**: 1–40 characters; avoid special characters that could be interpreted as injection
* **recvWindow**: Integer, 1–5000 ms; keep as small as possible (see [Replay Protection](../references/authentication.md#replay-protection))
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

**Place a market buy order (spend 100 USDT):**

```typescript
const order = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/spot/v1/trade/order", {
    symbol: "BTC-USDT",
    side: "BUY",
    type: "MARKET",
    quoteOrderQty: 100,
  }
);
// order.orderId, order.status, order.executedQty, order.cummulativeQuoteQty
```

**Place a limit sell order:**

```typescript
const order = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/spot/v1/trade/order", {
    symbol: "BTC-USDT",
    side: "SELL",
    type: "LIMIT",
    quantity: 0.001,
    price: 100000,
    timeInForce: "GTC",
  }
);
```

**Cancel an order:**

```typescript
await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/spot/v1/trade/cancel", {
    symbol: "BTC-USDT",
    orderId: 123456789,
  }
);
```

**Query open orders:**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/spot/v1/trade/openOrders", {
    symbol: "BTC-USDT",
  }
);
// data.orders[].orderId, data.orders[].price, data.orders[].status
```

**Query order history:**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/spot/v1/trade/historyOrders", {
    symbol: "BTC-USDT",
    pageIndex: 1,
    pageSize: 20,
  }
);
```

**Query trade fills for an order:**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/spot/v1/trade/myTrades", {
    symbol: "BTC-USDT",
    orderId: 123456789,
  }
);
// data.fills[].price, data.fills[].qty, data.fills[].commission
```

**Query commission rate:**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/spot/v1/user/commissionRate", {
    symbol: "BTC-USDT",
  }
);
// data.takerCommissionRate, data.makerCommissionRate
```

## Additional Resources

For full parameter descriptions, response schemas, and all 17 endpoints, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

All write operations (place order, cancel order, OCO create/cancel) require **CONFIRM** on `prod-live`. Read-only queries do not.

- **prod-live**: Ask user to type **CONFIRM** before any order placement or cancellation.
- **prod-vst**: No CONFIRM required. Inform user: "You are operating in the Production Simulated (VST) environment."

### Step 1 — Identify the Operation

If the user's intent is unclear, present options:

> What would you like to do?
> - Place a new order
> - Cancel an order / Cancel all orders
> - Check open orders
> - Check order history
> - Check trade fills (transaction details)
> - Check trading commission rate
> - OCO order (create / cancel / query)

### Step 2 — Collect symbol (if not provided)

> Please select a trading pair (or type another):
> - BTC-USDT
> - ETH-USDT
> - SOL-USDT
> - BNB-USDT
> - Other (format: BASE-USDT)

### Step 3 — Collect side (for order placement)

> Order direction:
> - BUY
> - SELL

### Step 4 — Collect order type

> Order type:
> - MARKET — execute immediately at best price
> - LIMIT — execute at a specific price (requires `price` and `timeInForce`)
> - TAKE_STOP_LIMIT — take-profit/stop-loss limit (requires `stopPrice` + `price`)
> - TAKE_STOP_MARKET — take-profit/stop-loss market (requires `stopPrice`)
> - TRIGGER_LIMIT — trigger limit order (requires `stopPrice` + `price`)
> - TRIGGER_MARKET — trigger market order (requires `stopPrice`)

### Step 5 — Collect quantity and price

- **MARKET BUY**: ask for `quoteOrderQty` (USDT to spend) or `quantity` (base asset amount)
- **MARKET SELL**: ask for `quantity` (base asset amount to sell)
- **LIMIT**: ask for `quantity` and `price`; confirm `timeInForce` (default GTC)
- **TAKE_STOP_LIMIT / TRIGGER_LIMIT**: ask for `quantity`, `stopPrice` (trigger), and `price` (execution)
- **TAKE_STOP_MARKET / TRIGGER_MARKET**: ask for `quantity` and `stopPrice`

### Step 6 — Confirm (prod-live only)

For `prod-live`, present a summary and ask:

> You are about to place the following order on **Production Live**:
> - Symbol: BTC-USDT
> - Side: BUY
> - Type: MARKET
> - Amount: 100 USDT
>
> Type **CONFIRM** to proceed, or anything else to cancel.

### Step 7 — Execute and report

Execute the API call and return the order ID, status, and filled quantity to the user.

---

### Cancel Order Flow

1. Ask for `symbol` and `orderId` (or `clientOrderID`) if not provided.
2. For `prod-live`: ask for **CONFIRM**.
3. Execute POST `/openApi/spot/v1/trade/cancel`.

### Cancel All Open Orders Flow

1. Ask for `symbol` (optional — omit to cancel all pairs).
2. For `prod-live`: ask for **CONFIRM**.
3. Execute POST `/openApi/spot/v1/trade/cancelOpenOrders`.

### OCO Order Flow

OCO (One-Cancels-the-Other) pairs a limit order with a stop-limit order; when one fills or triggers, the other is automatically cancelled.

1. Ask for `symbol`, `side`, `quantity`.
2. Ask for `limitPrice` (limit order execution price).
3. Ask for `triggerPrice` (stop-limit trigger price).
4. Ask for `orderPrice` (stop-limit execution price after trigger fires).
5. For `prod-live`: ask for **CONFIRM**.
6. Execute POST `/openApi/spot/v1/oco/order`.
