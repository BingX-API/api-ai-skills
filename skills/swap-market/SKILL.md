---
name: bingx-swap-market
description: Query BingX perpetual swap market data including ticker prices, order book depth, recent trades, funding rates, klines/candlesticks, open interest, mark price, and contract info. Use when the user asks about BingX swap or perpetual futures prices, order books, candlestick charts, funding rates, or market statistics.
---

# BingX Swap Market Data

Public market data for BingX perpetual futures. No special API KEY permission is needed, but all requests require `timestamp` + HMAC SHA256 `signature` + `X-BX-APIKEY` header. See [`references/authentication.md`](../references/authentication.md) for the signing process.

## Quick Reference

| Endpoint | Method | Description | Required | Optional |
|----------|--------|-------------|----------|----------|
| `/openApi/swap/v2/quote/contracts` | GET | All contract specifications | timestamp | symbol |
| `/openApi/swap/v1/tradingRules` | GET | Trading rules and specifications | timestamp, symbol | None |
| `/openApi/swap/v2/quote/depth` | GET | Order book bids & asks | timestamp, symbol | limit |
| `/openApi/swap/v2/quote/trades` | GET | Recent public trades | timestamp, symbol | limit |
| `/openApi/swap/v1/market/historicalTrades` | GET | Historical trade lookup | timestamp, symbol | limit, fromId |
| `/openApi/swap/v2/quote/premiumIndex` | GET | Mark price & premium index | timestamp | symbol |
| `/openApi/swap/v2/quote/fundingRate` | GET | Current & next funding rate | timestamp | symbol, startTime, endTime, limit |
| `/openApi/swap/v3/quote/klines` | GET | OHLCV candlestick data | timestamp, symbol, interval | startTime, endTime, limit |
| `/openApi/swap/v1/market/markPriceKlines` | GET | Mark price kline data | timestamp, symbol, interval | startTime, endTime, limit |
| `/openApi/swap/v2/quote/openInterest` | GET | Total open interest | timestamp, symbol | None |
| `/openApi/swap/v2/quote/ticker` | GET | 24h price change statistics | timestamp | symbol |
| `/openApi/swap/v1/ticker/price` | GET | Latest price ticker | timestamp | symbol |
| `/openApi/swap/v2/quote/bookTicker` | GET | Best bid/ask price & qty | timestamp, symbol | None |
| `/openApi/swap/v2/server/time` | GET | Query server time | timestamp | None |

---

## Parameters

### Common Parameters

* **timestamp**: Request timestamp in milliseconds (e.g., `1735693200000`). **Required for all endpoints.**
* **symbol**: Trading pair in `BASE-QUOTE` format (e.g., `BTC-USDT`, `ETH-USDT`, `SOL-USDT`)
* **limit**: Number of results to return. Default and max vary per endpoint.
* **startTime**: Start timestamp in milliseconds (e.g., `1735693200000`)
* **endTime**: End timestamp in milliseconds (e.g., `1735693200000`)
* **interval**: Kline/candlestick interval (see Enums below)
* **recvWindow**: Request validity window in milliseconds (optional, default `5000`, max `60000`)

### Enums

* **interval**: `1m` | `3m` | `5m` | `15m` | `30m` | `1h` | `2h` | `4h` | `6h` | `8h` | `12h` | `1d` | `3d` | `1w` | `1M`

### Parameter Validation Rules

* **symbol**: Must match `^[A-Z0-9]+-[A-Z]+$`; max 20 characters (e.g., `BTC-USDT`)
* **limit**: Positive integer; default and max vary per endpoint (typically 500–1000)
* **startTime** / **endTime**: Unix timestamps in milliseconds; `endTime` must be ≥ `startTime`
* **interval**: Must exactly match one of the enum values above
* **recvWindow**: Integer, 1–5000 ms (see [Replay Protection](../references/authentication.md#replay-protection))
* **timestamp**: Unix time in milliseconds; must be within `recvWindow` of server time

---

## Quick Start

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md)

**TypeScript helper:**

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

## Common Calls

**24h ticker price for BTC-USDT:**

```typescript
const ticker = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/quote/ticker", { symbol: "BTC-USDT" }
);
// ticker.lastPrice, ticker.priceChangePercent, ticker.volume
```

**Order book depth (top 20 levels):**

```typescript
const depth = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/quote/depth", { symbol: "BTC-USDT", limit: 20 }
);
// depth.bids: [price, qty][], depth.asks: [price, qty][]
```

**1-hour klines (last 100 candles):**

```typescript
const klines = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v3/quote/klines", { symbol: "BTC-USDT", interval: "1h", limit: 100 }
);
// Each item: [openTime, open, high, low, close, volume, closeTime]
```

**Current funding rate:**

```typescript
const funding = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/quote/fundingRate", { symbol: "BTC-USDT" }
);
// funding.fundingRate, funding.nextFundingTime
```

**Best bid/ask price:**

```typescript
const bookTicker = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/quote/bookTicker", { symbol: "BTC-USDT" }
);
// bookTicker.bidPrice, bookTicker.askPrice
```

## Additional Resources

For complete parameter descriptions, optional fields, and full response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

swap-market provides read-only market data. All requests require `timestamp` + HMAC SHA256 `signature` + `X-BX-APIKEY` header (no special API KEY permission needed). **No CONFIRM needed.** The interaction goal is to collect query parameters.

### Operation Identification

When the user's request is vague (e.g. "check the market" or "look at BTC"), first identify what type of data they want to query:

> Please select the market data type:
> - Price / 24h change — ticker
> - Best bid/ask price (top of book) — bookTicker
> - Order book depth — depth
> - K-lines / Candlesticks — klines
> - Funding rate — fundingRate
> - Mark price / Premium index — premiumIndex
> - Open interest — openInterest
> - Contract specification list — contracts

### When symbol is missing

Applicable endpoints: depth, trades, fundingRate, klines, openInterest

> Please select a trading pair (or type another):
> - BTC-USDT
> - ETH-USDT
> - SOL-USDT
> - BNB-USDT
> - Other (enter manually, format: BASE-USDT)

If the trading pair can be inferred from context (e.g. "BTC market today" or "Ethereum funding rate"), infer it automatically without asking again.

### When interval is missing (klines endpoint only)

> Please select a K-line interval:
> - 1m (1 minute)
> - 5m (5 minutes)
> - 15m (15 minutes)
> - 1h (1 hour)
> - 4h (4 hours)
> - 1d (daily)
> - 1w (weekly)

### limit handling

- klines: default 100, no need to ask — inform the user "returning the most recent 100 K-lines by default"
- depth: default 20, no need to ask

### Endpoints where symbol is optional

symbol is optional for ticker and premiumIndex (returns all contracts if omitted). bookTicker requires symbol. If the user does not specify a trading pair for ticker/premiumIndex, query all contracts and inform the user; if a trading pair is specified, query only that pair.
