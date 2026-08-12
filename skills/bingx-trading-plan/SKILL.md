---
name: bingx-trading-plan
description: Use when the user asks for a BingX perpetual futures trading plan, entry/exit strategy, position sizing, risk management, stop-loss/take-profit levels, or conservative/steady/aggressive plans. It builds a 6-dimension trade score from market data, technical analysis, funding, long-short ratios, top position long-short ratio, and liquidation heatmap pressure.
metadata:
  author: BingX
  version: "1.1.0"
  agent:
    requires:
      bins: ["python3"]
      python_packages: ["pandas", "numpy"]
      skills: ["bingx-swap-market", "bingx-technical-analysis"]
---

# BingX Trading Plan

**Base URLs:** `https://open-api.bingx.com`, `https://ox-bigdata-api.houtai.io` | **Authentication:** BingX public market endpoints do not require HMAC signing. Lindorm endpoints require platform-provided `access_token` and `proxy_user` headers; never hard-code credentials.

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/lindorm/v1/ai/kline/query` | POST | Lindorm query for long-short ratios and liquidation heatmap |
| `/api/lindorm/v1/ai/day/query` | POST | Lindorm daily query for Fear & Greed when needed |
| `/openApi/swap/v3/quote/klines` | GET | Klines for price context and ATR-style risk sizing |
| `/openApi/swap/v2/quote/premiumIndex` | GET | Funding rate for sentiment and crowding |
| `/openApi/swap/v2/quote/depth` | GET | Order book depth for entry context |

## Quick Start

```typescript
const BINGX_BASE_URL = "https://open-api.bingx.com";
const LINDORM_BASE_URL = "https://ox-bigdata-api.houtai.io";
const BASE_URLS = [BINGX_BASE_URL];

function isNetworkOrTimeout(error: unknown): boolean {
  if (!(error instanceof Error)) return false;
  return /fetch failed|network|timeout|aborted|ECONNRESET|ETIMEDOUT|ENOTFOUND/i.test(error.message);
}

async function fetchJson(url: string, init: RequestInit = {}): Promise<any> {
  const headers = new Headers(init.headers || {});
  if (url.startsWith(BINGX_BASE_URL)) {
    headers.set("X-SOURCE-KEY", "BX-AI-SKILL");
  }
  let lastError: unknown;
  for (const baseUrl of BASE_URLS) {
    try {
      const targetUrl = url.startsWith(BINGX_BASE_URL) ? url.replace(BINGX_BASE_URL, baseUrl) : url;
      const res = await fetch(targetUrl, { ...init, headers, signal: AbortSignal.timeout(10_000) });
      const data = await res.json();
      if (!res.ok) throw new Error(`BingX error HTTP ${res.status}: ${JSON.stringify(data)}`);
      if (data.code !== undefined && data.code !== 0) throw new Error(`BingX error ${data.code}: ${data.msg ?? JSON.stringify(data)}`);
      return data;
    } catch (error) {
      lastError = error;
      if (!isNetworkOrTimeout(error)) throw error;
    }
  }
  throw lastError instanceof Error ? new Error(`BingX error network: ${lastError.message}`) : new Error("BingX error network");
}

async function queryKlineLindorm(indicatorType: string, symbol = "BTCUSDT", interval = "4h", size = "20") {
  const accessToken = process.env.LINDORM_ACCESS_TOKEN;
  const proxyUser = process.env.LINDORM_PROXY_USER || "space_232";
  return fetchJson(`${LINDORM_BASE_URL}/api/lindorm/v1/ai/kline/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "access_token": accessToken || "",
      "proxy_user": proxyUser,
    },
    body: JSON.stringify({ indicatorType, symbol, interval, offset: "0", size }),
  });
}
```

## Common Calls

**Get global account long-short ratio:**
```typescript
const globalRatio = await queryKlineLindorm("global_ls_ratio", "BTCUSDT", "4h", "20");
```

**Get top account long-short ratio:**
```typescript
const topAccountRatio = await queryKlineLindorm("top_ls_ratio", "BTCUSDT", "4h", "20");
```

**Get top position long-short ratio:**
```typescript
const topPositionRatio = await queryKlineLindorm("top_position_ls_ratio", "BTCUSDT", "4h", "20");
```

**Get liquidation heatmap:**
```typescript
const coin = "BTCUSDT".replace(/USDT$/, "");
const liquidationHeatmap = await queryKlineLindorm("liquidation_aggregated_heatmap", coin, "3d", "100");
```

**Get funding rate:**
```typescript
const funding = await fetchJson(`${BINGX_BASE_URL}/openApi/swap/v2/quote/premiumIndex?symbol=BTC-USDT`);
```

**Get recent klines:**
```typescript
const klines = await fetchJson(
  `${BINGX_BASE_URL}/openApi/swap/v3/quote/klines?symbol=BTC-USDT&interval=4h&limit=120`
);
```

## Trigger Scenarios

| User intent | Parsed parameters |
|-------------|-------------------|
| "BTC trading plan" | `symbol=BTC-USDT`, `direction=auto`, `risk_tier=all` |
| "Can ETH go long?" | `symbol=ETH-USDT`, `direction=long`, `risk_tier=all` |
| "Aggressive SOL short plan" | `symbol=SOL-USDT`, `direction=short`, `risk_tier=aggressive` |
| "Conservative BTC plan with 10% account exposure" | `symbol=BTC-USDT`, `direction=auto`, `risk_tier=conservative`, `account_pct=10%` |

## Execution Steps

### Step 1 - Parse Intent

Extract:

| Parameter | Default | Description |
|-----------|---------|-------------|
| symbol | `BTC-USDT` | Trading pair |
| direction | `auto` | `auto`, `long`, or `short` |
| risk_tier | `all` | `all`, `conservative`, `steady`, or `aggressive` |
| account_pct | unset | Optional account exposure mentioned by the user |

Convert the Lindorm symbol to the compact format, for example `BTC-USDT` to `BTCUSDT`.

### Step 2 - Collect Data

Collect available data in parallel:

| Signal | Source | Status |
|--------|--------|--------|
| Price, funding, klines, depth | `bingx-swap-market` endpoints | Available |
| Technical score, support, resistance | `bingx-technical-analysis` | Available |
| Global long-short ratio | Lindorm `global_ls_ratio` | Available |
| Top account long-short ratio | Lindorm `top_ls_ratio` | Available |
| Top position long-short ratio | Lindorm `top_position_ls_ratio` | Available |
| Liquidation heatmap | Lindorm `liquidation_aggregated_heatmap` | Available as coin-level aggregated data |

The Lindorm kline query accepts `symbol` and `interval`. Use the user-requested symbol when available. If a requested interval returns empty data, fall back to the default synced interval for that indicator. Current known defaults are `4h` for long-short ratios and `3d` for liquidation heatmap.

For liquidation heatmap, current available data is coin-level aggregated data. Convert the compact pair to a coin symbol, for example `BTCUSDT` to `BTC`, and query `liquidation_aggregated_heatmap` with `interval=3d`. This is suitable for identifying major liquidation zones, but it cannot distinguish exchange-level, contract-level, or pair-level liquidation structure.

### Step 3 - Build 6-Dimension Score

```bash
python3 scripts/scoring.py \
  --symbol {symbol} \
  --ta-result '{technical_analysis_json}' \
  --market-data '{market_data_json}' \
  --sentiment-data '{lindorm_sentiment_json}'
```

Expected `sentiment-data` can include:

```json
{
  "global_account_long_short_ratio": 1.27,
  "top_account_long_short_ratio": 1.38,
  "top_position_long_short_ratio": 1.54,
  "liqAbove": 320000,
  "liqBelow": 120000,
  "liquidation_note": "Aggregated coin-level heatmap is used; pair-level liquidation structure is not available."
}
```

### Step 4 - Generate Risk Plans

```bash
python3 scripts/plan.py \
  --symbol {symbol} \
  --direction {direction} \
  --risk-tier {risk_tier} \
  --score-result '{score_json}' \
  --current-price {price} \
  --support-resistance '{support_resistance_json}'
```

### Step 5 - Present Output

Provide conservative, steady, and aggressive plans unless the user asks for a specific tier.

## Direction Rules

| Condition | Direction |
|-----------|-----------|
| User explicitly requests long or short | Use the requested direction and warn if it conflicts with the score |
| `auto` and score > +30 | LONG |
| `auto` and score < -30 | SHORT |
| `auto` and -29 <= score <= +29 | NEUTRAL; suggest waiting and provide reference plans only |

## Risk Profile Reference

| Profile | Risk | Entry | Stop Loss | Take Profit | Leverage | Position |
|---------|------|-------|-----------|-------------|----------|----------|
| conservative | Low | Limit order near support or resistance | 2.0x ATR-style distance | Single target around 3R | up to 3x | 1% account |
| steady | Medium | Limit or market order | 1.5x ATR-style distance | TP1 2R and TP2 3R | 3x to 10x | 2% account |
| aggressive | High | Market momentum entry | 1.0x ATR-style distance | TP1 1.5R, TP2 2R, TP3 3R plus trailing stop | 10x to 20x | 3% to 5% account |

## Output Template

```
{symbol} 6-Dimension Trading Score: {score}/100 ({label})

Trend           {score_trend}       {signal}
Momentum        {score_momentum}    {signal}
Volume          {score_volume}      {signal}
Funding         {score_funding}     {signal}
Long/Short      {score_sentiment}   {signal}
Liquidation     {score_liq}         {signal_or_data_note}

Overall View: {LONG/SHORT/NEUTRAL} (confidence: {HIGH/MEDIUM/LOW})

Conservative Plan
- Entry zone: ${entry_low} - ${entry_high}
- Stop loss: ${stop_loss}
- Take profit: ${tp1}
- Leverage: up to 3x
- Position: 1% account

Steady Plan
- Entry zone: ${entry_low} - ${entry_high}
- Stop loss: ${stop_loss}
- Take profit: TP1 ${tp1}, TP2 ${tp2}
- Leverage: 3x - 10x
- Position: 2% account

Aggressive Plan
- Entry zone: ${entry_low} - ${entry_high}
- Stop loss: ${stop_loss}
- Take profit: TP1 ${tp1}, TP2 ${tp2}, TP3 ${tp3}, trailing stop
- Leverage: 10x - 20x
- Position: 3% - 5% account

Data Notes
{fallback or data-quality notes, if any}

This is a market analysis reference, not investment advice. Control risk and respect stop loss.
```

## Agent Interaction Rules

- This skill produces analysis only. It must not place, cancel, or modify orders.
- Do not depend on a separate market sentiment skill; collect long-short ratio signals through Lindorm.
- Use Lindorm `global_ls_ratio` for global account long-short ratio.
- Use Lindorm `top_ls_ratio` only as top account long-short ratio. Do not label it as top position long-short ratio.
- Use Lindorm `top_position_ls_ratio` for top position long-short ratio.
- Use Lindorm `liquidation_aggregated_heatmap` for coin-level aggregated liquidation heatmap and disclose that pair-level liquidation structure is not available.
- Current Lindorm data is synchronized for Binance only. Do not expose exchange selection.
