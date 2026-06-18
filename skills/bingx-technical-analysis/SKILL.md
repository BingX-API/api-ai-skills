---
name: bingx-technical-analysis
description: >
  Use this skill when the user asks for technical analysis, indicator values
  (RSI, MACD, EMA, Bollinger Bands, KDJ, SuperTrend, etc.), candlestick
  pattern recognition, multi-timeframe scoring, support/resistance levels,
  divergence detection, or any request like "analyze BTC", "BTC technical",
  "should I open a position", "bull/bear analysis", "indicator analysis",
  "candlestick patterns", "trend analysis".
  Depends on bingx-swap-market for K-line data. Computes 78 indicators +
  62 candlestick patterns locally via pandas-ta-classic.
metadata:
  author: BingX
  version: "1.0.0"
  agent:
    requires:
      bins: ["python3"]
      python_packages: ["pandas-ta-classic", "scipy", "pandas"]
---

# BingX Technical Analysis

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

## Quick Reference

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/openApi/swap/v3/quote/klines` | GET | OHLCV kline data | Yes |
| `/openApi/swap/v2/quote/premiumIndex` | GET | Funding rate & mark price | Yes |
| `/openApi/swap/v2/quote/openInterest` | GET | Open interest | Yes |

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

**Fetch klines for technical analysis (200 candles, 4h):**

```typescript
const klines = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v3/quote/klines", { symbol: "BTC-USDT", interval: "4h", limit: 200 }
);
```

**Fetch funding rate:**

```typescript
const funding = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/quote/premiumIndex", { symbol: "BTC-USDT" }
);
```

**Fetch open interest:**

```typescript
const oi = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/quote/openInterest", { symbol: "BTC-USDT" }
);
```

---

## Trigger Conditions

Activate this skill when the user says any of the following:
- "Analyze BTC", "BTC technical analysis", "BTC-USDT 4h analysis"
- "What is the RSI", "MACD signal", "Bollinger Band position"
- Any indicator name + symbol
- "Bull/bear analysis", "trend analysis", "candlestick patterns"
- "Where is support/resistance", "any divergence"

## Execution Steps

### Step 1: Parse User Intent

Extract from user input:
- symbol: trading pair (default BTC-USDT)
- interval: kline interval (default 4h)
- mode: analysis mode
  - "full"      — full analysis (indicators + patterns + score + support/resistance)
  - "indicator" — single indicator query (e.g. "what is RSI")
  - "pattern"   — candlestick pattern recognition
  - "score"     — composite score only

### Step 2: Fetch Kline Data

Call bingx-swap-market to get OHLCV:

  GET /openApi/swap/v3/quote/klines
    symbol={symbol}, interval={interval}, limit=200

If mode=score (multi-timeframe required), fetch 4 intervals in parallel: 15m, 1h, 4h, 1d

Also fetch auxiliary data:
  GET /openApi/swap/v2/quote/premiumIndex  (funding rate)
  GET /openApi/swap/v2/quote/openInterest  (open interest)

### Step 3: Run Calculation Script

Pass kline JSON to the Python script (located in the skill's scripts/ directory):

  python3 scripts/analyze.py \
    --mode {mode} \
    --symbol {symbol} \
    --interval {interval} \
    --klines '{klines_json}'

Script returns a structured JSON result.

### Step 4: Format Output

Organize output based on mode:

  full      — full analysis report (see output template below)
  indicator — single indicator value + signal + one-line interpretation
  pattern   — list of recently identified patterns
  score     — composite score + multi-timeframe overview

### Step 5: Disclaimer

Always append at the end of every output:
  ⚠️ Technical analysis is based on historical data only and does not constitute investment advice.

---

## Output Templates

### Full Mode

```
📊 {symbol} {interval} Technical Analysis

━━ Composite Score ━━
{total}/100 — {label}
  Trend {trend}/100 | Momentum {momentum}/100 | Volume {volume}/100 | Pattern {pattern}/100

━━ Multi-Timeframe ━━
  15m: {score_15m}({label_15m}) | 1h: {score_1h}({label_1h}) | 4h: {score_4h}({label_4h}) | 1d: {score_1d}({label_1d})

━━ Key Indicators ━━
  RSI(14)      {rsi_value}   {rsi_signal}
  MACD         {histogram}   {macd_signal}   {macd_detail}
  EMA          {ema_detail}
  ADX          {adx_value}   {adx_signal}
  Supertrend   {st_signal}   {st_value}
  BB %B        {pctb}        {bb_detail}

━━ Candlestick Patterns ━━
  {pattern_list or "No significant patterns detected in the last 5 candles"}

━━ Divergence ━━
  RSI: {rsi_div} | MACD: {macd_div} | OBV: {obv_div}

━━ Support / Resistance ━━
  ▲ {r1} — {r1_type}
  ● {current_price} — current price
  ▼ {s1} — {s1_type}

⚠️ Technical analysis is based on historical data only and does not constitute investment advice.
```

### Indicator Mode

```
{symbol} {interval} {indicator_name} = {value}
Signal: {signal} — {one_line_interpretation}
```

### Pattern Mode

```
{symbol} {interval} Recent Candlestick Patterns:
  ● {pattern_name} — {bars_ago} bars ago, {type} signal

{bullish_count} bullish and {bearish_count} bearish patterns detected in the last 5 candles.
```

### Score Mode

```
{symbol} Composite Score: {total}/100 — {label}

Multi-Timeframe Overview:
  15m: {score_15m} {label_15m} | 1h: {score_1h} {label_1h} | 4h: {score_4h} {label_4h} | 1d: {score_1d} {label_1d}

{one-line summary of multi-timeframe confluence}
```

---

## Agent Interaction Rules

**Parameter security.** Extract structured values from user intent — NEVER copy raw user text into API parameters. Validate symbol format (`^[A-Z0-9]+-[A-Z]+$`) and interval against allowed values before calling the API.

All endpoints used by this skill are **read-only market data queries**. No CONFIRM required in any environment.

When the user's request is vague (e.g. "analyze BTC"), default to `mode=full` and `interval=4h`. If mode can be inferred from keywords ("RSI" → indicator, "pattern" → pattern, "score" → score), infer it automatically without asking.

## Error Handling

- Invalid symbol: prompt user to check the trading pair format (e.g. BTC-USDT)
- Insufficient kline data (< 50 candles): inform user, suggest switching to a longer interval
- Python ModuleNotFoundError (pandas-ta-classic): prompt user to run `pip install pandas-ta-classic scipy pandas` and retry
- Other Python script errors: show friendly message with error summary, suggest retry
- Network timeout: suggest retry later
