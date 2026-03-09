---
name: bingx-spot-market
description: Query BingX spot market data including ticker prices, order book depth, recent trades, klines/candlesticks, and trading symbol info. Use when the user asks about BingX spot prices, order books, candlestick charts, recent trades, or spot market statistics.
---

# BingX Spot Market Data

Public market data for BingX spot trading. No authentication required.

## Quick Reference

| Endpoint | Method | Description | Required | Optional | Authentication |
|----------|--------|-------------|----------|----------|----------------|
| `/openApi/spot/v1/common/symbols` | GET | Spot trading symbol specifications | None | symbol | No |
| `/openApi/spot/v1/market/depth` | GET | Order book bids & asks | symbol | limit | No |
| `/openApi/spot/v2/market/depth` | GET | Aggregated order book (with precision) | symbol, depth, type | None | No |
| `/openApi/spot/v1/market/trades` | GET | Recent public trades | symbol | limit | No |
| `/openApi/spot/v2/market/kline` | GET | OHLCV candlestick data | symbol, interval | startTime, endTime, limit | No |
| `/openApi/spot/v1/ticker/24hr` | GET | 24h price change statistics | None | symbol | No |
| `/openApi/spot/v2/ticker/price` | GET | Latest price ticker | symbol | None | No |
| `/openApi/spot/v1/ticker/bookTicker` | GET | Best bid/ask price & qty | symbol | None | No |
| `/openApi/market/his/v1/kline` | GET | Historical kline data | symbol, interval | startTime, endTime, limit | No |
| `/openApi/market/his/v1/trade` | GET | Historical trade lookup | symbol | limit, fromId | No |

---

## Parameters

### Common Parameters

* **symbol**: Trading pair in `BASE-USDT` format (e.g., `BTC-USDT`, `ETH-USDT`, `SOL-USDT`). Note: the order book aggregation endpoint (`/openApi/spot/v2/market/depth`) uses underscore format `BTC_USDT`.
* **limit**: Number of results to return. Default and max vary per endpoint.
* **startTime**: Start timestamp in milliseconds (e.g., `1735693200000`)
* **endTime**: End timestamp in milliseconds (e.g., `1735779600000`)
* **interval**: Kline/candlestick interval (see Enums below)

### Enums

* **interval**: `1m` | `3m` | `5m` | `15m` | `30m` | `1h` | `2h` | `4h` | `6h` | `8h` | `12h` | `1d` | `3d` | `1w` | `1M`
* **type** (order book aggregation precision): `step0` | `step1` | `step2` | `step3` | `step4` | `step5`

### Parameter Validation Rules

* **symbol**: Must match `^[A-Z0-9]+-[A-Z]+$` (e.g., `BTC-USDT`); depth endpoint uses `BTC_USDT` (underscore)
* **limit**: Positive integer; default and max vary per endpoint
* **startTime** / **endTime**: Unix timestamps in milliseconds; `endTime` must be ≥ `startTime`
* **interval**: Must exactly match one of the enum values above
* **type**: When used, must be one of `step0`–`step5`

---

## Quick Start

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md)

**TypeScript helper:**

```typescript
// Base URLs — see references/base-urls.md for all environments
const BASE_URLS = ["https://open-api.bingx.com", "https://open-api.bingx.pro"];

async function fetchSpotMarket(
  path: string,
  params: Record<string, string | number> = {}
): Promise<unknown> {
  const query = new URLSearchParams(
    Object.entries(params).map(([k, v]) => [k, String(v)])
  ).toString();
  for (const base of BASE_URLS) {
    try {
      const url = `${base}${path}${query ? `?${query}` : ""}`;
      const res = await fetch(url, {
        headers: { "X-SOURCE-KEY": "BX-AI-SKILL" },
      });
      const json = await res.json();
      if (json.code !== 0) throw new Error(`BingX error ${json.code}: ${json.msg}`);
      return json.data;
    } catch (e) {
      if (base === BASE_URLS[BASE_URLS.length - 1]) throw e;
    }
  }
}
```

## Common Calls

**24h ticker for BTC-USDT:**

```typescript
const ticker = await fetchSpotMarket("/openApi/spot/v1/ticker/24hr", {
  symbol: "BTC-USDT",
});
// ticker[0].lastPrice, ticker[0].priceChangePercent, ticker[0].volume
```

**Latest price:**

```typescript
const price = await fetchSpotMarket("/openApi/spot/v2/ticker/price", {
  symbol: "BTC-USDT",
});
// price[0].trades[0].price
```

**Order book depth (top 20 levels):**

```typescript
const depth = await fetchSpotMarket("/openApi/spot/v1/market/depth", {
  symbol: "BTC-USDT",
  limit: 20,
});
// depth.bids: [price, qty][], depth.asks: [price, qty][]
```

**1-hour klines (last 100 candles):**

```typescript
const klines = await fetchSpotMarket("/openApi/spot/v2/market/kline", {
  symbol: "BTC-USDT",
  interval: "1h",
  limit: 100,
});
// Each item: [openTime, open, high, low, close, volume, closeTime, quoteVolume]
```

**Best bid/ask price:**

```typescript
const bookTicker = await fetchSpotMarket("/openApi/spot/v1/ticker/bookTicker", {
  symbol: "BTC-USDT",
});
// bookTicker[0].bidPrice, bookTicker[0].askPrice
```

**Recent trades:**

```typescript
const trades = await fetchSpotMarket("/openApi/spot/v1/market/trades", {
  symbol: "BTC-USDT",
  limit: 50,
});
// trades[0].price, trades[0].qty, trades[0].time
```

## Additional Resources

For complete parameter descriptions, optional fields, and full response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

spot-market provides public read-only market data. No authentication required, **no CONFIRM needed**. The interaction goal is to collect query parameters.

### Operation Identification

When the user's request is vague (e.g. "check spot market" or "look at BTC price"), first identify what type of data they want to query:

> Please select the market data type:
> - Price / 24h change — ticker/24hr
> - Latest trade price — ticker/price
> - Best bid/ask price (top of book) — bookTicker
> - Order book depth — depth
> - K-lines / Candlesticks — kline
> - Recent trades — trades
> - Historical K-lines — historical kline
> - Historical trades — historical trades
> - Trading pair specification list — symbols

### When symbol is missing

Applicable endpoints: depth, trades, kline, ticker/price, bookTicker, historical kline, historical trades

> Please select a trading pair (or type another):
> - BTC-USDT
> - ETH-USDT
> - SOL-USDT
> - BNB-USDT
> - Other (enter manually, format: BASE-USDT)

If the trading pair can be inferred from context (e.g. "BTC market today" or "Ethereum price"), infer it automatically without asking again.

### When interval is missing (kline endpoint only)

> Please select a K-line interval:
> - 1m (1 minute)
> - 5m (5 minutes)
> - 15m (15 minutes)
> - 1h (1 hour)
> - 4h (4 hours)
> - 1d (daily)
> - 1w (weekly)

### limit handling

- kline: default 100, no need to ask — inform the user "returning the most recent 100 K-lines by default"
- depth: default 20, no need to ask
- trades: default 100, no need to ask

### Endpoints where symbol is optional

symbol is optional for ticker/24hr (returns all trading pairs if omitted). bookTicker and price ticker require symbol. If the user does not specify a trading pair for ticker/24hr, query all pairs and inform the user; if a trading pair is specified, query only that pair.
