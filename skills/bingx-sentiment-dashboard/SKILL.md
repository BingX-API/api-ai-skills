---
name: bingx-sentiment-dashboard
description: Use when the user asks about market sentiment, Fear & Greed Index, funding rate heatmap, OI anomalies, AHR999, DCA zone, or overall market mood.
metadata:
  author: BingX
  version: "2.1.0"
  agent:
    requires:
      bins: ["python3", "curl"]
      python_packages: ["pandas", "matplotlib", "seaborn", "numpy"]
      skills: ["bingx-swap-market"]
---

# BingX Sentiment Dashboard

**Base URLs:** `https://open-api.bingx.com`, `https://api.alternative.me` | **Auth:** No authentication required. No HMAC SHA256 signing is required. BingX market requests should include `X-SOURCE-KEY: BX-AI-SKILL`; alternative.me requires no custom headers.

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| https://api.alternative.me/fng/ | GET | Fear & Greed Index with replaceable `limit` |
| /openApi/swap/v2/quote/premiumIndex | GET | Funding rates for all symbols |
| /openApi/swap/v2/quote/openInterest | GET | Open interest for a symbol |
| /openApi/swap/v3/quote/klines | GET | BTC daily klines for local AHR999 calculation |

## Quick Start

```typescript
const BINGX_BASE_URL = "https://open-api.bingx.com";
const FEAR_GREED_BASE_URL = "https://api.alternative.me";
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

async function fetchFearGreed(limit = 10) {
  return fetchJson(`${FEAR_GREED_BASE_URL}/fng/?limit=${limit}`);
}
```

## Common Calls

**Get funding rates for the market:**
```typescript
const funding = await fetchJson(`${BINGX_BASE_URL}/openApi/swap/v2/quote/premiumIndex`);
```

**Get open interest for a symbol:**
```typescript
const oi = await fetchJson(`${BINGX_BASE_URL}/openApi/swap/v2/quote/openInterest?symbol=BTC-USDT`);
```

**Get BTC daily klines for local AHR999 calculation:**
```typescript
const klines = await fetchJson(
  `${BINGX_BASE_URL}/openApi/swap/v3/quote/klines?symbol=BTC-USDT&interval=1d&limit=200`
);
```

**Get Fear & Greed Index:**
```typescript
const fearGreed = await fetchFearGreed(10);
// limit is replaceable. Example response: { name, data: [{ value, value_classification, timestamp }], metadata }
```

## Trigger Scenarios

| Mode | Trigger examples | Description |
|------|------------------|-------------|
| full | "market sentiment", "overall market mood" | Full sentiment dashboard with available dimensions |
| fear_greed | "fear and greed index", "is the market panicking" | Fear & Greed only |
| funding | "funding rate heatmap", "which coins have high funding" | Funding rate overview |
| oi | "OI anomaly", "open interest changes" | OI anomaly detection |
| ahr999 | "AHR999", "good time to DCA into BTC" | AHR999 index |

## Execution Steps

### Step 1 - Parse Intent

Determine `mode` from the trigger table. Default to `full`.

### Step 2 - Collect Available Data

| Dimension | Source | Status |
|-----------|--------|--------|
| Fear & Greed Index | `https://api.alternative.me/fng/?limit={limit}` | Available |
| Funding Rate Heatmap | BingX `/openApi/swap/v2/quote/premiumIndex` | Available |
| OI Anomaly Detection | BingX `/openApi/swap/v2/quote/openInterest` plus ticker price changes | Available with available symbols |
| AHR999 | Local calculation from BTC daily klines via `bingx-swap-market` | Available |

For Fear & Greed, use `limit=10` by default. Replace `limit` when the user asks for a different history length.

### Step 3 - Fetch Fear & Greed

```bash
python3 scripts/fear_greed.py --limit 10
```

Pass the result JSON as `--fear-greed`.

### Step 4 - Compute AHR999

```bash
python3 scripts/ahr999.py \
  --btc-kline '{btc_daily_kline_json}'
```

Pass the result JSON as `--ahr999-result`.

### Step 5 - Compute Sentiment Score

```bash
python3 scripts/sentiment.py \
  --mode {mode} \
  --fear-greed '{fear_greed_json_or_empty}' \
  --funding '{funding_json}' \
  --oi '{oi_json}' \
  --tickers '{tickers_json}' \
  --ahr999-result '{ahr999_result_json}'
```

### Step 6 - Generate Funding Heatmap

```bash
python3 scripts/heatmap.py \
  --funding '{funding_json}' \
  --output ~/.bingx-skills/sentiment/funding_heatmap.png
```

If rendering fails, output the top funding rates as text.

### Step 7 - Detect OI Anomalies

```bash
python3 scripts/oi_alert.py \
  --oi '{oi_json}' \
  --tickers '{tickers_json}'
```

### Step 8 - Present Output

Report each available dimension independently, then provide the composite score from available dimensions only.

## Output Template

```
Market Sentiment Dashboard

Composite Sentiment: {score}/100 ({label})

Fear & Greed   {fg_score_or_na}   {fg_detail}
Funding Rate   {fr_score}         {funding_detail}
OI Change      {oi_score}         {oi_detail}
AHR999         {ahr_score}        {ahr999_detail}

Top 5 Funding Rates
{top5 extreme funding rate symbols}

OI Anomalies
{anomaly list, or "No significant OI anomalies detected from available data"}

Data Notes
{unavailable dimensions, if any}
```

## Agent Interaction Rules

- Keep the dashboard to four dimensions only: Fear & Greed, funding rate heatmap, OI anomaly detection, and AHR999.
- Use `https://api.alternative.me/fng/?limit={limit}` for Fear & Greed Index. Default `limit` is `10`.
- If one dimension is unavailable, still output the remaining dimensions and reweight the composite score by available dimensions.
- AHR999 is computed locally from BTC daily klines via `bingx-swap-market`; do not require a backend AHR999 lab code.
- The skill is read-only and must not place, cancel, or modify orders.
