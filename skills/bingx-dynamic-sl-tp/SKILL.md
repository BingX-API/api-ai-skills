---
name: bingx-dynamic-sl-tp
description: >
  Use this skill when the user asks to set, adjust, or optimize stop-loss
  and take-profit, or any request like "set stop-loss", "set take-profit", "place stop-loss",
  "dynamic stop-loss", "trailing take-profit", "Trailing Stop", "partial take-profit",
  "where should I set my stop-loss", "volatility stop-loss", "ATR stop-loss",
  "break-even stop", "trailing stop".
  Dynamically calculates SL/TP based on ATR, volatility, and support/resistance.
  Supports trailing stop, partial take-profit, and break-even stop.
  Depends on bingx-swap-market and bingx-swap-trade.
metadata:
  author: BingX
  version: "1.0.0"
  agent:
    requires:
      bins: ["python3"]
      python_packages: ["pandas", "pandas-ta-classic"]
      skills: ["bingx-swap-market", "bingx-swap-trade"]
---

# BingX Dynamic SL/TP

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

## Quick Reference

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/openApi/swap/v3/quote/klines` | GET | Kline data for ATR calculation | Yes |
| `/openApi/swap/v2/trade/order` | POST | Place conditional SL/TP order | Yes |
| `/openApi/swap/v2/trade/order` | DELETE | Cancel existing SL/TP order | Yes |

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

**Fetch klines for ATR / support-resistance calculation (200 candles, 4h):**

```typescript
const klines = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v3/quote/klines", { symbol: "BTC-USDT", interval: "4h", limit: 200 }
);
```

---

## Trigger Conditions

Activate this skill when the user says any of the following:
- "Help me set SL/TP", "set stop-loss", "place stop-loss order"
- "Dynamic stop-loss", "trailing take-profit", "Trailing Stop", "trailing stop"
- "Partial take-profit", "take profit in 3 batches"
- "Where should I set my stop-loss", "ATR stop-loss", "volatility stop-loss"
- "Move stop-loss to break-even"

---

## Execution Steps

### Step 1 — Parse User Intent

| mode | Trigger example | Description |
|------|----------------|-------------|
| set | "Help me set SL/TP" | Calculate and set SL/TP for current position |
| adjust | "Move stop-loss to break-even" | Adjust existing SL/TP |
| trailing | "Enable trailing stop" | Set Trailing Stop |
| partial | "Partial take-profit" | Close position in batches |
| recommend | "Where should I set my stop-loss" | Calculate recommended levels only, do not execute |

Parameter extraction:

| Parameter | Default | Description |
|-----------|---------|-------------|
| symbol | Auto-fetch from current position | Trading pair |
| strategy | atr | Stop-loss strategy (atr/volatility/structure/fixed_pct) |
| atr_multiplier | 1.5 | ATR multiplier |
| tp_mode | levels | Take-profit mode (ratio/levels/trailing/breakeven/hybrid) |
| risk_reward | 2.0 | Risk-reward ratio |

---

### Step 2 — Fetch Position & Market Data

1. Call bingx-swap-trade to query current position (direction, avg entry price, quantity, leverage)
2. Call bingx-swap-market to fetch klines (4h, 200 candles, for ATR + support/resistance calculation)

If no position: prompt "No open position found. Would you like to pre-calculate SL/TP levels?" and switch to recommend mode.
If multiple positions: let user select one or set SL/TP one by one.

---

### Step 3 — Calculate SL/TP

```bash
python3 scripts/calculator.py \
  --direction {long/short} \
  --entry-price {price} \
  --strategy {strategy} \
  --atr-multiplier {multiplier} \
  --tp-mode {tp_mode} \
  --risk-reward {rr} \
  --klines '{klines_json}'
```

---

### Step 4 — Safety Confirmation

Present to the user:
- Current position details
- Calculated SL/TP levels + estimated PnL amounts
- Types of conditional orders to be placed

Execute only after user confirmation. **Do NOT place orders without confirmation.**

---

### Step 5 — Place Orders

Via bingx-swap-trade:
- Automatically cancel existing conditional orders before placing new ones, no duplicates
- Stop-loss: conditional order (market trigger)
- Take-profit: conditional order or Trailing Stop
- Partial take-profit: multiple conditional orders (different prices + different quantities)

---

### Step 6 — Output Result (per output template)

---

## Output Templates

### Set Mode

```
**Smart SL/TP Plan**

Current Position: {symbol} {direction}
Entry Price: ${entry_price} | Qty: {qty} | Leverage: {leverage}x

**Stop-Loss** ({strategy} x {atr_multiplier})
- Level: ${sl_price} ({sl_pct}%)
- Estimated loss: -${risk_amount}

**Take-Profit** ({tp_mode})
TP1  ${tp1_price} ({tp1_pct}%)  {tp1_split}% of position  +${tp1_reward}
TP2  ${tp2_price} ({tp2_pct}%)  {tp2_split}% of position  +${tp2_reward}
TP3  {trailing/price}            {tp3_split}% of position  let profits run

Risk-Reward Ratio: 1:{risk_reward}
{if applicable} Stop-loss will be moved to break-even (${entry_price}) after TP1 fills.

**Confirm execution? (yes/no)**
```

### Recommend Mode

```
**SL/TP Recommended Levels**

{symbol} {direction} (entry ${entry_price})

Strategy         Stop-Loss     Distance  Notes
ATR x 1.5       ${sl_atr15}   {pct}%    Standard, recommended
ATR x 1.0       ${sl_atr10}   {pct}%    Tight stop
Structure stop  ${sl_struct}  {pct}%    Beyond prior low/high

Take-Profit  Level    R:R
1R           ${tp1}   1:1
2R           ${tp2}   1:2
3R           ${tp3}   1:3

For reference only. Say "help me set SL/TP" to place the orders.
```

---

## Agent Interaction Rules

**Parameter security.** Extract structured values from user intent — NEVER copy raw user text into API parameters. Validate symbol and numeric parameters before use.

Kline queries are read-only and require no CONFIRM. All order placements (SL/TP conditional orders) require explicit user confirmation.

- **prod-live**: Require user to type **CONFIRM** before placing or cancelling any SL/TP orders.
- **prod-vst**: No CONFIRM required. Inform user they are in the simulated environment.

When mode is `recommend`, only calculate and display levels — do NOT place any orders.

## Error Handling

- No position: inform user and switch to recommend mode
- Order placement failed: show error code, suggest retry
- Position already closed: inform user the position no longer exists
- Insufficient kline data: suggest switching to a longer interval
