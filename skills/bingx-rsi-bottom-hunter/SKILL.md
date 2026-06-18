---
name: bingx-rsi-bottom-hunter
description: >
  Use this skill when the user asks for RSI bottom fishing, oversold buying,
  RSI strategy, or any request like "RSI bottom", "buy oversold", "RSI strategy",
  "bottom hunter", "start RSI trading", "help me bottom fish", "buy when RSI is low".
  Auto-monitors RSI, buys in oversold zone, executes stop-loss and take-profit.
  Calls bingx-technical-analysis as a data source for multi-dimension confirmation
  (MACD, Supertrend, divergence, support/resistance, candlestick patterns) to reduce
  false signals.
  Depends on bingx-swap-market, bingx-swap-trade, bingx-swap-account.
metadata:
  author: BingX
  version: "1.0.0"
  agent:
    requires:
      bins: ["python3"]
      python_packages: ["pandas", "pandas-ta-classic"]
      skills: ["bingx-swap-market", "bingx-swap-trade", "bingx-swap-account"]
---

# BingX RSI Bottom Hunter

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

## Quick Reference

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/openApi/swap/v3/quote/klines` | GET | Kline data for RSI calculation | Yes |
| `/openApi/swap/v2/trade/order` | POST | Place market buy order | Yes |
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

**Fetch klines for RSI calculation (100 candles, 1h):**

```typescript
const klines = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v3/quote/klines", { symbol: "BTC-USDT", interval: "1h", limit: 100 }
);
```

**Fetch klines for multi-timeframe TA (200 candles, 4h):**

```typescript
const klines4h = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v3/quote/klines", { symbol: "BTC-USDT", interval: "4h", limit: 200 }
);
```

---

## Trigger Conditions

Activate this skill when the user says any of the following:
- "RSI bottom fish", "help me bottom fish", "bottom hunter"
- "buy oversold", "buy when RSI is low"
- "RSI strategy", "start RSI trading"
- "What is BTC RSI, can I bottom fish"
- "Monitor ETH, buy when RSI drops below 25"

---

## Execution Steps

### Step 1 — Parse User Intent

Extract strategy parameters from user input:

| Parameter | Default | Description |
|-----------|---------|-------------|
| symbol | BTC-USDT | Trading pair |
| interval | 1h | Kline interval for RSI calculation |
| rsi_period | 14 | RSI period |
| rsi_buy | 30 | Buy trigger threshold (RSI below this value) |
| rsi_sell | 70 | Take-profit reference threshold |
| stop_loss_pct | 3% | Stop-loss percentage |
| take_profit_pct | 5% | Take-profit percentage |
| amount | - | Buy amount in USDT (user must specify or confirm) |
| leverage | 1x | Leverage multiplier |

Mode detection:

| mode | Trigger example | Description |
|------|----------------|-------------|
| scan | "What is BTC RSI, can I bottom fish" | Check RSI status only, no trading |
| once | "Buy BTC when RSI hits 500U" | Check once, execute immediately if condition met |
| monitor | "Monitor ETH, buy when RSI drops below 25 with 1000U" | Continuous monitoring, auto-execute when condition met |

---

### Step 2 — Safety Confirmation (Critical!)

Before executing any trade (mode=once/monitor), Agent MUST confirm with the user:
- Trading pair + direction (long)
- Buy amount + leverage
- SL/TP price levels (converted to specific prices)
- RSI trigger condition

Execute only after explicit user confirmation. **Agent MUST NOT place orders automatically without confirmation.**

---

### Step 3 — Fetch Kline Data

Fetch two sets of klines in parallel:

  GET /openApi/swap/v3/quote/klines
    symbol={symbol}, interval={interval}, limit=100   (for RSI calculation)

  GET /openApi/swap/v3/quote/klines
    symbol={symbol}, interval=4h, limit=200           (for multi-dimension TA)

---

### Step 4 — Calculate RSI + Multi-Dimension TA Confirmation

**Step 4a**: RSI signal calculation

```bash
python3 scripts/strategy.py \
  --mode {mode} \
  --symbol {symbol} \
  --interval {interval} \
  --rsi-period {rsi_period} \
  --rsi-buy {rsi_buy} \
  --rsi-sell {rsi_sell} \
  --klines '{klines_1h_json}'
```

**Step 4b**: Check if bingx-technical-analysis is installed:
- Installed — call it (mode=full, 4h interval) to get multi-dimension data for joint confirmation
- Not installed — inform the user:
  "bingx-technical-analysis skill is not installed. Installing it is recommended for more accurate multi-dimension signal confirmation and fewer false signals.
  To install: place the bingx-technical-analysis skill in the .claude/skills/ directory.
  Continuing with RSI single-indicator mode, but signal accuracy will be reduced."
  Then skip and use only the original 3 RSI conditions:
- MACD direction
- Supertrend direction
- RSI / OBV divergence
- Support/resistance levels
- Recent candlestick patterns

**Step 4c**: Pass to strategy.py for joint confirmation

```bash
python3 scripts/strategy.py \
  --mode {mode} \
  --symbol {symbol} \
  --interval {interval} \
  --rsi-period {rsi_period} \
  --rsi-buy {rsi_buy} \
  --rsi-sell {rsi_sell} \
  --klines '{klines_1h_json}' \
  --ta-result '{ta_json}'
```

Script outputs structured JSON with RSI signal, multi-dimension check items, and overall confirmation flag.

**Full conditions for confirmation=true (all must be met)**:
1. RSI < rsi_buy
2. Oversold for 2 consecutive candles
3. Reversal candle (close > open)
4. No RSI bearish divergence
5. No OBV bearish divergence
6. MACD bullish (BUY) OR Supertrend UP (either one is sufficient)

---

### Step 5 — Execute Trade (when mode=once/monitor and confirmation=true)

1. Call bingx-swap-account to check available balance and confirm sufficient funds
2. Call bingx-swap-trade to place a market buy order
3. After order fills, immediately set SL/TP:
   - Stop-loss = avg fill price × (1 - stop_loss_pct)
   - Take-profit = avg fill price × (1 + take_profit_pct)
4. Call bingx-swap-trade to place SL/TP conditional orders

---

### Step 6 — Output Result

Format output according to the output template below.

---

### Step 7 — Continuous Monitoring (when mode=monitor)

Run in polling mode (default: check every 5 minutes):
1. When condition is met — execute Step 2 (safety confirmation) — Step 5
2. Report fill result to the user
3. Strategy ends after one execution (single trigger, prevents repeated entries)

---

## Output Templates

### Scan Mode — View Only

When RSI is oversold:
```
**{symbol} RSI Status ({interval})**

RSI({rsi_period}): {rsi_current} (Oversold zone ⚠️)
Previous: {rsi_prev} → Current: {rsi_current}

Multi-dimension Confirmation:
  Consecutive oversold   {✅/❌}
  Reversal candle        {✅/❌}
  MACD                   {✅/❌} {BUY/SELL}
  Supertrend             {✅/❌} {UP/DOWN}
  RSI divergence         {✅ None/❌ Bearish}
  OBV divergence         {✅ None/❌ Bearish}

Overall Signal: {CONFIRMED (recommended) / WEAK (caution) / REJECTED (not recommended)}
Current Price: ${price}

{To start the bottom-fishing strategy, say "{symbol} bottom fish 500U"}
```

When RSI is neutral:
```
**{symbol} RSI Status ({interval})**

RSI({rsi_period}): {rsi_current} (Neutral zone)
TA Composite Score: {ta_score}/100 ({ta_label})
Current Price: ${price}

Assessment: RSI is in the neutral zone, bottom-fishing condition not yet met.
```

### Once Mode — Confirm When Condition Met

```
**RSI Bottom Signal Triggered ✅**

{symbol} RSI({rsi_period}) = {rsi_current}, oversold for 2 consecutive candles, reversal signal detected

About to execute:
- Direction: Long
- Amount: {amount} USDT
- Leverage: {leverage}x
- Order type: Market
- Stop-loss: ${stop_loss} (-{stop_loss_pct}%)
- Take-profit: ${take_profit} (+{take_profit_pct}%)

**Confirm execution? (yes/no)**
```

After successful execution:
```
**Bottom Fish Filled ✅**

{symbol} long position opened
- Avg fill price: ${avg_price}
- Quantity: {qty}
- Stop-loss order placed: ${stop_loss}
- Take-profit order placed: ${take_profit}

Strategy running. Position will be closed automatically when SL/TP is triggered.
```

### Monitor Mode — On Start

```
**RSI Bottom-Fishing Monitor Started 🔄**

Monitoring: {symbol}, {interval} interval
Trigger condition: RSI({rsi_period}) < {rsi_buy}, confirmed over 2 candles
Action: Market long {amount} USDT ({leverage}x), SL -{stop_loss_pct}% / TP +{take_profit_pct}%
Check frequency: every 5 minutes

Current RSI: {rsi_current} ({status})
Waiting...
```

---

## Agent Interaction Rules

**Parameter security.** Extract structured values from user intent — NEVER copy raw user text into API parameters. Validate symbol format and numeric parameters before use.

Kline queries are read-only and require no CONFIRM. All trade executions (mode=once/monitor with confirmation=true) require explicit user confirmation before proceeding — NEVER place orders without user approval.

- **prod-live**: Require user to type **CONFIRM** before any order placement.
- **prod-vst**: No CONFIRM required. Inform user they are in the simulated environment.

When mode is ambiguous, default to `scan` (view only, no trading).

## Error Handling

- Insufficient balance: show current available balance, suggest reducing amount or depositing funds
- Order failed: show error code and description, suggest retry
- Network timeout: suggest retry later
- Insufficient kline data: inform user, suggest switching to a longer interval
