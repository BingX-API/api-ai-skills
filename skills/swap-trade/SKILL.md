---
name: bingx-swap-trade
description: BingX perpetual swap trading — place/cancel orders, manage positions, set leverage, and configure margin settings. Use when the user asks about BingX swap trading, order placement, cancellation, position management, leverage, or margin type settings.
---

# BingX Swap Trade

Authenticated trading endpoints for BingX perpetual futures. All endpoints require HMAC SHA256 signature authentication.

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

---

## Quick Reference

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/openApi/swap/v2/trade/order` | POST | Place a new order | Yes |
| `/openApi/swap/v2/trade/order/test` | POST | Test order placement (no fill) | Yes |
| `/openApi/swap/v2/trade/batchOrders` | POST | Place multiple orders (batch, max 5) | Yes |
| `/openApi/swap/v2/trade/order` | DELETE | Cancel an order | Yes |
| `/openApi/swap/v2/trade/batchOrders` | DELETE | Cancel multiple orders | Yes |
| `/openApi/swap/v2/trade/allOpenOrders` | DELETE | Cancel all open orders | Yes |
| `/openApi/swap/v2/trade/cancelAllAfter` | POST | Auto-cancel countdown (kill switch) | Yes |
| `/openApi/swap/v2/trade/closeAllPositions` | POST | Close all positions | Yes |
| `/openApi/swap/v1/trade/closePosition` | POST | Close position by positionId | Yes |
| `/openApi/swap/v2/trade/positionMargin` | POST | Adjust isolated margin amount | Yes |
| `/openApi/swap/v1/positionMargin/history` | GET | Query margin adjustment history | Yes |
| `/openApi/swap/v2/trade/openOrders` | GET | Query open orders | Yes |
| `/openApi/swap/v2/trade/openOrder` | GET | Query a single open order | Yes |
| `/openApi/swap/v2/trade/order` | GET | Query an order by ID | Yes |
| `/openApi/swap/v1/trade/fullOrder` | GET | Query full order details | Yes |
| `/openApi/swap/v2/trade/allOrders` | GET | Query all historical orders | Yes |
| `/openApi/swap/v2/trade/forceOrders` | GET | Query liquidation/ADL orders | Yes |
| `/openApi/swap/v2/trade/allFillOrders` | GET | Query trade fill history | Yes |
| `/openApi/swap/v2/trade/fillHistory` | GET | Query historical trade fill details | Yes |
| `/openApi/swap/v1/twap/openOrders` | GET | Query open TWAP orders | Yes |
| `/openApi/swap/v1/twap/historyOrders` | GET | Query TWAP order history | Yes |
| `/openApi/swap/v1/twap/orderDetail` | GET | Query TWAP order details | Yes |
| `/openApi/swap/v1/twap/order` | POST | Create TWAP order | Yes |
| `/openApi/swap/v1/twap/cancelOrder` | POST | Cancel TWAP order | Yes |
| `/openApi/swap/v1/trade/positionHistory` | GET | Query position history | Yes |
| `/openApi/swap/v1/maintMarginRatio` | GET | Query maintenance margin ratio | Yes |
| `/openApi/swap/v2/trade/marginType` | GET | Query margin type | Yes |
| `/openApi/swap/v2/trade/marginType` | POST | Set margin type (ISOLATED/CROSSED) | Yes |
| `/openApi/swap/v2/trade/leverage` | GET | Query current leverage | Yes |
| `/openApi/swap/v2/trade/leverage` | POST | Set leverage | Yes |
| `/openApi/swap/v1/positionSide/dual` | GET | Query position mode | Yes |
| `/openApi/swap/v1/positionSide/dual` | POST | Set position mode | Yes |
| `/openApi/swap/v1/trade/assetMode` | GET | Query asset mode (single/multi-asset) | Yes |
| `/openApi/swap/v1/trade/assetMode` | POST | Set asset mode (single/multi-asset) | Yes |
| `/openApi/swap/v1/trade/multiAssetsRules` | GET | Query multi-asset margin rules | Yes |
| `/openApi/swap/v1/user/marginAssets` | GET | Query margin assets for multi-asset mode | Yes |
| `/openApi/swap/v1/trade/autoAddMargin` | POST | Set auto-add margin for position | Yes |
| `/openApi/swap/v1/trade/reverse` | POST | Reverse position (one-click flip) | Yes |
| `/openApi/swap/v1/trade/cancelReplace` | POST | Cancel and replace an order (atomic) | Yes |
| `/openApi/swap/v1/trade/batchCancelReplace` | POST | Batch cancel and replace orders | Yes |
| `/openApi/swap/v1/trade/amend` | POST | Modify an existing open order | Yes |
| `/openApi/swap/v2/trade/getVst` | POST | Get VST (virtual simulation trading) | Yes |

---

## Parameters

### Order Parameters

* **symbol**: Trading pair in `BASE-QUOTE` format (e.g., `BTC-USDT`, `ETH-USDT`)
* **side**: Order direction — `BUY` or `SELL`
* **positionSide**: Position direction — `LONG` or `SHORT` (hedge mode) / `BOTH` (one-way mode)
* **type**: Order type (see Enums)
* **quantity**: Order quantity in **coins** (e.g., `0.01` for BTC-USDT); can be omitted when `closePosition: true`
* **price**: Limit price (required for `LIMIT`, `STOP`, `TAKE_PROFIT` types)
* **stopPrice**: Trigger price (required for `STOP_MARKET`, `STOP`, `TAKE_PROFIT_MARKET`, `TAKE_PROFIT`)
* **timeInForce**: `GTC` | `IOC` | `FOK` | `PostOnly` — default `GTC`; required for `LIMIT` type
* **clientOrderId**: Custom order ID, 1–40 chars (converted to lowercase)
* **recvWindow**: Request validity window in milliseconds (max 60000)
* **orderId**: System order ID (for cancel/query operations)
* **workingType**: Price source used to trigger conditional orders — `MARK_PRICE` (mark price) or `CONTRACT_PRICE` (last traded price, default)
* **stopGuaranteed**: `true` | `false` — Whether stop-loss execution is guaranteed; guaranteed stops may incur an additional fee
* **closePosition**: `true` | `false` — When the trigger fires, close the **entire** position quantity; cannot be used with `quantity`
* **reduceOnly**: `true` | `false` — Order can only reduce (never increase) position size
* **activationPrice**: Activation price for `TRAILING_STOP_MARKET` orders (optional; defaults to current market price when omitted)
* **priceRate**: Trailing callback rate for `TRAILING_STOP_MARKET` / `TRAILING_TP_SL` orders (e.g., `0.05` = 5%)
* **stopLoss**: JSON-string query parameter — Attach a stop-loss to a `MARKET`/`LIMIT` order. Build and validate the nested object first, then call `JSON.stringify` exactly once.
* **takeProfit**: JSON-string query parameter — Attach a take-profit to a `MARKET`/`LIMIT` order. Build and validate the nested object first, then call `JSON.stringify` exactly once.

### Position Parameters

* **leverage**: Integer leverage multiplier (e.g., `10`, `20`, `50`)
* **marginType**: `ISOLATED` or `CROSSED`
* **dualSidePosition**: `"true"` (hedge mode) or `"false"` (one-way mode)
* **positionId**: Position ID string (used by `closePosition` and `positionMargin` endpoints)
* **amount**: Margin adjustment amount in USDT (used by `positionMargin` endpoint)
* **direction_type**: `1` (add margin) or `2` (reduce margin) (used by `positionMargin` endpoint)

### Enums

**type** (Order type):
- `MARKET` — Market order (fills immediately at best price; attach `stopLoss`/`takeProfit` objects here)
- `LIMIT` — Limit order (requires `price` and `timeInForce`; attach `stopLoss`/`takeProfit` objects here)
- `STOP_MARKET` — Stop-loss market (triggers at `stopPrice`, executes as market)
- `STOP` — Stop-loss limit (triggers at `stopPrice`, executes as limit at `price`)
- `TAKE_PROFIT_MARKET` — Take-profit market (triggers at `stopPrice`, executes as market)
- `TAKE_PROFIT` — Take-profit limit (triggers at `stopPrice`, executes as limit at `price`)
- `TRAILING_STOP_MARKET` — Trailing stop market; uses `priceRate` (required) and optional `activationPrice`
- `TRAILING_TP_SL` — Trailing TP/SL for an **existing** position; links to position via `symbol` + `positionSide`; uses `priceRate`

**side**: `BUY` | `SELL`

**positionSide**: `LONG` | `SHORT` | `BOTH`

**marginType**: `ISOLATED` | `CROSSED`

**timeInForce**: `GTC` | `IOC` | `FOK` | `PostOnly`

**workingType** (trigger price source for conditional orders):
- `MARK_PRICE` — Use mark price to evaluate trigger condition
- `CONTRACT_PRICE` — Use last traded price (default)

### Stop-Loss / Take-Profit Object Structure

When attaching `stopLoss` or `takeProfit` to a `MARKET` or `LIMIT` order:

```json
{
  "stopLoss": {
    "type": "STOP_MARKET",       // "STOP_MARKET" or "STOP"
    "stopPrice": 29000,          // required: trigger price
    "price": 28900,              // required only for type "STOP" (limit execution price)
    "workingType": "MARK_PRICE", // "MARK_PRICE" or "CONTRACT_PRICE"
    "stopGuaranteed": false      // true = guaranteed execution (extra fee may apply)
  },
  "takeProfit": {
    "type": "TAKE_PROFIT_MARKET",  // "TAKE_PROFIT_MARKET" or "TAKE_PROFIT"
    "stopPrice": 35000,            // required: trigger price
    "price": 35100,                // required only for type "TAKE_PROFIT" (limit execution price)
    "workingType": "MARK_PRICE",
    "stopGuaranteed": false
  }
}
```

> **Constraint:** `stopLoss`/`takeProfit` objects are **only** supported on `MARKET` or `LIMIT` order types. They cannot be used with `STOP_MARKET`, `STOP`, `TAKE_PROFIT_MARKET`, `TAKE_PROFIT`, `TRAILING_STOP_MARKET`, or `TRAILING_TP_SL`.

The outer `stopLoss` and `takeProfit` values are query parameters containing JSON strings. Inside that JSON, `stopPrice` and optional `price` must be JSON numbers, not quoted numeric strings. Never send `{"stopPrice":"63538.3"}`.

### Parameter Validation Rules

Before sending a request, validate parameters client-side to avoid unnecessary API errors:

* **symbol**: Must match `^[A-Z0-9]+-[A-Z]+$`; max 20 characters (e.g., `BTC-USDT`)
* **quantity**: Must be a positive number (> 0); max precision depends on the symbol's contract specification
* **price**: When provided, must be a positive number (> 0)
* **stopPrice**: When provided, must be a positive number (> 0); must differ from current market price
* **stopLoss.stopPrice / takeProfit.stopPrice**: Required JSON numbers; convert with `Number(...)`, then require a finite value greater than 0
* **stopLoss.price / takeProfit.price**: Optional JSON numbers; when provided, convert with `Number(...)`, then require a finite value greater than 0
* **stopLoss / takeProfit serialization**: Validate the nested object before serializing it. The signed query value must be the exact `JSON.stringify(...)` result
* **leverage**: Positive integer; range varies per symbol (typically 1–125 for BTC-USDT)
* **clientOrderId**: Alphanumeric only, 1–40 characters; pattern `^[a-zA-Z0-9]{1,40}$`; no special characters
* **priceRate**: Trailing callback rate; must satisfy 0 < value ≤ 1 (e.g., `0.05` = 5%)
* **recvWindow**: Integer, 1–5000 ms; keep as small as possible (see [Replay Protection](../references/authentication.md#replay-protection))
* **timestamp**: Unix time in milliseconds; must be within `recvWindow` of server time

---

## Quick Start

> **CONSTRAINT**: You MUST copy the `fetchSigned` function below verbatim
> when generating code. Do NOT rewrite the signing, request, or JSON parsing
> logic. Only modify: (1) `BASE` URL entries for custom environments,
> (2) business parameters passed to `fetchSigned`. For the full client with
> URL-encoding and JSON body support, see
> [`references/authentication.md`](../references/authentication.md).

```typescript
import * as crypto from "crypto";
import JSONBig from "json-bigint";
const JSONBigParse = JSONBig({ storeAsString: true });
// Full signing details & edge cases → references/authentication.md
// Domain priority: .com is mandatory primary; .pro is fallback for network/timeout errors ONLY.
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
function toPositiveNumber(value: unknown, field: string): number {
  const numberValue = Number(value);
  if (!Number.isFinite(numberValue) || numberValue <= 0) {
    throw new Error(`${field} must be a finite positive number`);
  }
  return numberValue;
}
function normalizeAttachedOrder(
  key: "stopLoss" | "takeProfit", value: unknown
): string {
  let parsed: unknown = value;
  if (typeof value === "string") {
    try { parsed = JSON.parse(value); }
    catch { throw new Error(`${key} must be valid JSON`); }
  }
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error(`${key} must be an object or a JSON object string`);
  }
  const nested = { ...(parsed as Record<string, unknown>) };
  const allowedTypes = key === "stopLoss"
    ? new Set(["STOP_MARKET", "STOP"])
    : new Set(["TAKE_PROFIT_MARKET", "TAKE_PROFIT"]);
  if (typeof nested.type !== "string" || !allowedTypes.has(nested.type)) {
    throw new Error(`${key}.type is invalid`);
  }
  nested.stopPrice = toPositiveNumber(nested.stopPrice, `${key}.stopPrice`);
  if (nested.price !== undefined) {
    nested.price = toPositiveNumber(nested.price, `${key}.price`);
  }
  if (nested.workingType !== undefined &&
      nested.workingType !== "MARK_PRICE" &&
      nested.workingType !== "CONTRACT_PRICE") {
    throw new Error(`${key}.workingType is invalid`);
  }
  if (nested.stopGuaranteed !== undefined &&
      typeof nested.stopGuaranteed !== "boolean") {
    throw new Error(`${key}.stopGuaranteed must be a boolean`);
  }
  return JSON.stringify(nested);
}
function normalizeParams(params: Record<string, unknown>): Record<string, unknown> {
  const normalized = { ...params };
  if (normalized.price !== undefined) {
    normalized.price = toPositiveNumber(normalized.price, "price");
  }
  for (const key of ["stopLoss", "takeProfit"] as const) {
    if (normalized[key] !== undefined) {
      normalized[key] = normalizeAttachedOrder(key, normalized[key]);
    }
  }
  return normalized;
}
function serializeParamValue(value: unknown): string {
  if (value !== null && typeof value === "object") return JSON.stringify(value);
  return String(value);
}
function validateParams(params: Record<string, unknown>): void {
  const FORBIDDEN = /[&=?#\r\n]/;
  for (const [k, v] of Object.entries(params)) {
    const s = serializeParamValue(v);
    if (FORBIDDEN.test(s)) throw new Error(`Param "${k}" has forbidden char in: "${s}"`);
  }
}
async function fetchSigned(env: string, apiKey: string, secretKey: string,
  method: "GET" | "POST" | "DELETE", path: string, params: Record<string, unknown> = {}
) {
  const urls = BASE[env] ?? BASE["prod-live"];
  const normalized = normalizeParams(params);
  const all = { ...normalized, timestamp: Date.now() };
  validateParams(all);
  const qs = Object.keys(all).sort()
    .map(k => `${k}=${serializeParamValue(all[k])}`).join("&");
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
        signal: AbortSignal.timeout(10000),
      });
      const json = JSONBigParse.parse(await res.text());
      if (json.code !== 0) throw new Error(`BingX error ${json.code}: ${json.msg}`);
      return json.data;
    } catch (e) {
      if (!isNetworkOrTimeout(e) || base === urls[urls.length - 1]) throw e;
    }
  }
}
```

### Code Usage Rules

- **MUST** copy `fetchSigned` verbatim -- do not simplify or rewrite
- **MUST** use `json-bigint` (`JSONBigParse.parse`) for response parsing -- not `JSON.parse`
- **MUST** include `X-SOURCE-KEY: BX-AI-SKILL` header on every request
- **MUST NOT** remove the domain fallback loop or `isNetworkOrTimeout` check
- **MUST** normalize and serialize all business parameters before creating the timestamp and signature. If any parameter changes, discard the previous timestamp/signature and sign a new request
- **MUST NOT** interpolate object values directly with `${params[k]}`; object values must be serialized with `JSON.stringify`, otherwise they become `[object Object]`

---

## Common Calls

**Place a market buy order:**

```typescript
const order = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/swap/v2/trade/order", {
    symbol: "BTC-USDT",
    side: "BUY",
    positionSide: "LONG",
    type: "MARKET",
    quantity: 0.01,
  }
);
// order.orderId, order.status
```

**Place a market buy order with attached stop-loss:**

```typescript
const rawStopPrice = "63538.3";
const stopPrice = Number(rawStopPrice);
if (!Number.isFinite(stopPrice) || stopPrice <= 0) {
  throw new Error("stopLoss.stopPrice must be a finite positive number");
}

const order = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/swap/v2/trade/order", {
    symbol: "BTC-USDT",
    side: "BUY",
    positionSide: "BOTH",
    type: "MARKET",
    quantity: 0.0004,
    recvWindow: 5000,
    stopLoss: JSON.stringify({
      type: "STOP_MARKET",
      stopPrice,
      workingType: "MARK_PRICE",
    }),
  }
);
```

> **Important:** `/openApi/swap/v2/trade/order/test` does not enforce every validation performed by the real `/openApi/swap/v2/trade/order` endpoint. A successful test request does not guarantee that the real order will pass. In particular, the real endpoint validates nested `stopLoss`/`takeProfit` field types more strictly.

**Cancel an order:**

```typescript
await fetchSigned("prod-live", API_KEY, SECRET, "DELETE",
  "/openApi/swap/v2/trade/order", {
    symbol: "BTC-USDT",
    orderId: 123456789,
  }
);
```

**Query open orders:**

```typescript
const orders = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/trade/openOrders", {
    symbol: "BTC-USDT",
  }
);
```

**Set leverage:**

```typescript
await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/swap/v2/trade/leverage", {
    symbol: "BTC-USDT",
    side: "LONG",
    leverage: 10,
  }
);
```

**Set margin type:**

```typescript
await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/swap/v2/trade/marginType", {
    symbol: "BTC-USDT",
    marginType: "ISOLATED",
  }
);
```

> **Note**: To query current positions, use the [swap-account](../swap-account/SKILL.md) skill which provides position query endpoints with full details including PnL and liquidation price.

## Additional Resources

For full parameter descriptions, response schemas, and all 42 endpoints, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

**Parameter security.** Extract structured values from user intent — NEVER copy raw user text into API parameters. Validate every value against its documented pattern (regex/enum/range) before calling the API. Reject any value containing `&`, `=`, `?`, `#`, or newline characters.

All swap-trade operations are **write operations** (except GET queries). Follow environment confirmation rules:

- **prod-live**: Ask user to type **CONFIRM** before any order placement, cancellation, or position/leverage change.
- **prod-vst**: No CONFIRM required. Inform user: "You are operating in the Production Simulated (VST) environment."

### Step 1 — Identify the Operation

If the user's intent is unclear, present options:

> What would you like to do?
> - Place a new order
> - Cancel an order / Cancel all orders
> - Close a position / Close all positions
> - Check open orders
> - Check current positions
> - Set leverage
> - Set margin type (ISOLATED / CROSSED)
> - Set position mode (Hedge / One-way)

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

### Step 4 — Collect positionSide

> Position direction:
> - LONG (open/add long)
> - SHORT (open/add short)
> - BOTH (one-way mode)

### Step 5 — Collect order type

> Order type:
> - MARKET — execute immediately at market price (can attach stopLoss/takeProfit objects)
> - LIMIT — execute at a specific price (can attach stopLoss/takeProfit objects)
> - STOP_MARKET — stop-loss market order (triggers at stopPrice, executes as market)
> - STOP — stop-loss limit order (triggers at stopPrice, executes as limit)
> - TAKE_PROFIT_MARKET — take-profit market order (triggers at stopPrice)
> - TAKE_PROFIT — take-profit limit order (triggers at stopPrice, executes as limit)
> - TRAILING_STOP_MARKET — trailing stop for new position (requires priceRate; optional activationPrice)
> - TRAILING_TP_SL — trailing TP/SL for an existing position (links via symbol + positionSide; requires priceRate)

### Step 6 — Collect quantity and price

- Ask for quantity in **coins** (e.g., 0.01 BTC for BTC-USDT). Omit if using `closePosition: true`.
- If type is `LIMIT`, `STOP`, or `TAKE_PROFIT`: also ask for `price`.
- If type is `STOP_MARKET`, `STOP`, `TAKE_PROFIT_MARKET`, or `TAKE_PROFIT`: also ask for `stopPrice`.
- If type is `TRAILING_STOP_MARKET` or `TRAILING_TP_SL`: ask for `priceRate` (e.g., 0.05 = 5%) and optionally `activationPrice`.
- If type is `MARKET` or `LIMIT`: optionally offer to attach a `stopLoss` and/or `takeProfit` object (ask for trigger price and type).

**Optional advanced parameters** (ask only if relevant or user mentions them):
- `workingType`: trigger price source — `MARK_PRICE` or `CONTRACT_PRICE` (default)
- `reduceOnly`: `true` to ensure the order only reduces position size
- `closePosition`: `true` to close the entire position when triggered (cannot use with `quantity`)
- `stopGuaranteed`: `true` for guaranteed stop execution (extra fee may apply)

### Step 7 — Confirm (prod-live only)

For `prod-live` environment, present a summary and ask:

> You are about to place the following order on **Production Live**:
> - Symbol: BTC-USDT
> - Side: BUY / LONG
> - Type: MARKET
> - Quantity: 0.01
>
> Type **CONFIRM** to proceed, or anything else to cancel.

### Step 8 — Execute and report

Execute the API call and return the order ID and status to the user.

---

### Cancel Order Flow

1. Ask for `orderId` (or `clientOrderId`) if not provided.
2. For `prod-live`: ask for **CONFIRM**.
3. Execute DELETE `/openApi/swap/v2/trade/order`.

### Close Position Flow

1. Ask for symbol if not provided.
2. Present options: close specific position (LONG/SHORT) or close all.
3. For `prod-live`: ask for **CONFIRM**.
4. Use POST `/openApi/swap/v2/trade/closeAllPositions` or place a reverse MARKET order.

### Leverage Settings Flow

1. Ask for symbol if not provided.
2. Ask for position side (LONG / SHORT / both).
3. Ask for leverage value (e.g., 1–125).
4. For `prod-live`: ask for **CONFIRM**.
5. Execute POST `/openApi/swap/v2/trade/leverage`.

### Margin Type Flow

1. Ask for symbol if not provided.
2. Present options: ISOLATED or CROSSED.
3. For `prod-live`: ask for **CONFIRM**.
4. Execute POST `/openApi/swap/v2/trade/marginType`.

### Position Mode Flow

1. Present options: Hedge mode (`dualSidePosition: true`) or One-way mode (`dualSidePosition: false`).
2. For `prod-live`: ask for **CONFIRM**.
3. Execute POST `/openApi/swap/v1/positionSide/dual`.
