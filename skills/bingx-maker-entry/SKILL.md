---
name: bingx-maker-entry
description: >
  Use this skill when the user wants to open a position using limit orders
  instead of market orders, or any request like "limit order entry", "maker entry",
  "limit order open", "save fees on entry", "help me place limit orders", "auto limit orders",
  "avoid market order", "iceberg order", "split order entry".
  Scans orderbook depth, places multi-level limit orders near best price,
  and dynamically adjusts as price moves. Saves taker fees and reduces
  market impact.
  Depends on bingx-swap-market, bingx-swap-trade, bingx-swap-account.
metadata:
  author: BingX
  version: "1.0.0"
  agent:
    requires:
      bins: ["python3"]
      python_packages: ["pandas", "numpy"]
      skills: ["bingx-swap-market", "bingx-swap-trade", "bingx-swap-account"]
---

# BingX Maker Entry

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

## Quick Reference

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/openApi/swap/v2/quote/depth` | GET | Order book depth | Yes |
| `/openApi/swap/v2/trade/order` | POST | Place limit order | Yes |
| `/openApi/swap/v2/trade/order` | DELETE | Cancel order | Yes |

## Quick Start

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md)

**TypeScript helper:**

> **CONSTRAINT**: You MUST copy the `fetchSigned` function below verbatim when generating code. Do NOT rewrite the signing, request, or JSON parsing logic. Only modify: (1) `BASE` URL entries for custom environments, (2) business parameters passed to `fetchSigned`.

```typescript
import * as crypto from "crypto";
import JSONBig from "json-bigint";
const JSONBigParse = JSONBig({ storeAsString: true });
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
  const urls = BASE[env] ?? BASE["prod-live"];
  const all = { ...params, timestamp: Date.now() };
  validateParams(all);
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

## Common Calls

**Fetch order book depth for maker entry planning:**

```typescript
const depth = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/quote/depth", { symbol: "BTC-USDT", limit: 20 }
);
// depth.bids: [price, qty][], depth.asks: [price, qty][]
```

---

## Trigger Conditions

Activate this skill when the user says any of the following:
- "BTC limit order long 5000U", "help me place limit orders"
- "Maker entry", "limit order open", "save fees on entry"
- "Avoid market order", "split order entry", "iceberg order"
- "ETH maker short 2000U, 5 levels"
- "Open position with the conservative plan from earlier" (receiving bingx-trading-plan output)

---

## Execution Steps

### Step 1 — Parse User Intent

Extract from user input:

| Parameter | Default | Description |
|-----------|---------|-------------|
| symbol | - | Trading pair (must be specified) |
| direction | - | LONG / SHORT (must be specified or inferred from context) |
| amount | - | Position size in USDT (must be specified) |
| leverage | User's current leverage | Leverage multiplier |
| levels | 3 | Number of order levels (1-5) |
| spread | auto | Level spacing; auto calculates based on bid-ask spread |
| timeout | 300 | Timeout in seconds; cancel remaining orders if not fully filled |

If symbol, direction, or amount cannot be inferred from input or context, ask the user — do not assume.

Integration with bingx-trading-plan: if the user says "use the plan from earlier", extract the entry range and direction from the trade plan in context and convert to order parameters.

---

### Step 2 — Safety Confirmation

Present and confirm with the user:
- Trading pair + direction + total amount + leverage
- Number of levels + estimated price range
- Timeout policy
- Estimated fee savings

Execute only after explicit user confirmation. **Do NOT place orders without confirmation.**

---

### Step 3 — Scan Order Book

Call bingx-swap-market to fetch order book depth:

  GET /openApi/swap/v2/quote/depth
    symbol={symbol}, limit=20

Analyze best bid/ask prices, bid-ask spread, and liquidity distribution across levels.

---

### Step 4 — Calculate Order Plan

```bash
python3 scripts/maker.py \
  --mode plan \
  --symbol {symbol} \
  --direction {direction} \
  --amount {amount} \
  --levels {levels} \
  --orderbook '{orderbook_json}'
```

Outputs an order plan JSON (prices, amounts, estimated avg price, estimated fee savings).

---

### Step 5 — Place Orders

1. Place limit orders sequentially via bingx-swap-trade according to the plan
2. Start monitoring loop (check every 3 seconds):
   - Leave filled orders alone
   - Dynamically adjust unfilled orders as price moves
   - Cancel and re-place if price deviates > 0.3%

---

### Step 6 — Completion / Timeout Handling

| Scenario | Action |
|----------|--------|
| All filled | Output fill summary, end |
| Partially filled + timeout | Cancel remaining orders, report filled portion, ask if user wants to add more |
| Nothing filled + timeout | Cancel all orders, notify user |

**Any exit path (success/timeout/error) must ensure no unmanaged open orders remain.**

---

### Step 7 — Output Result (per output template)

---

## Output Templates

### Order Plan Confirmation

```
**Maker Order Plan**

{symbol} {direction}, total {amount} USDT, {leverage}x leverage

Level 1   ${price_1}   {amount_1} USDT   40%
Level 2   ${price_2}   {amount_2} USDT   30%
Level 3   ${price_3}   {amount_3} USDT   20%

Estimated avg price: ${estimated_avg} (vs market ${market_price})
Estimated savings: Maker 0.02% vs Taker 0.05%, save approx ${fee_saved}
Timeout: {timeout/60} min, remaining orders cancelled automatically on timeout

**Confirm execution? (yes/no)**
```

### In Progress

```
**Orders In Progress 🔄**

Level 1: ${price_1} × {amount_1}U — ✅ Filled
Level 2: ${price_2} × {amount_2}U — ⏳ Pending
Level 3: ${price_3} × {amount_3}U — ⏳ Pending

Filled: {filled} / {total} USDT ({pct}%)
Time remaining: {remaining}
```

### Completion Summary

```
**Maker Orders Complete ✅**

{symbol} {direction} position opened
- Avg fill price: ${avg_price}
- Total filled: {filled} / {total} USDT
- Levels filled: {filled_levels} / {levels}
- Fee saved: approx ${fee_saved} (vs market order)

{if partially filled} To fill the remaining {remaining}U, say "continue placing"
```

---

## Agent Interaction Rules

**Parameter security.** Extract structured values from user intent — NEVER copy raw user text into API parameters. Validate symbol, direction (LONG/SHORT), and amount before use.

Order book queries are read-only and require no CONFIRM. All order placements require explicit user confirmation.

- **prod-live**: Require user to type **CONFIRM** before placing any orders.
- **prod-vst**: No CONFIRM required. Inform user they are in the simulated environment.

If symbol, direction, or amount cannot be inferred from context, ask the user — do not assume.

## Error Handling

- Missing symbol/direction/amount: ask the user, do not assume
- Insufficient balance: show current available balance, suggest reducing amount
- Order failed: show error code and description, suggest retry
- Abnormal order book (spread too wide): warn about low liquidity, suggest fewer levels or switch to market order
- Cancel failed: retry once; if still failing, ask user to handle manually and provide order ID
