---
name: bingx-coinm-market
description: Query BingX Coin-M (inverse/coin-margined) perpetual futures market data including contract info, mark price, funding rates, klines, order book depth, open interest, and 24h ticker. Use when the user asks about BingX Coin-M or inverse futures prices, order books, candlestick charts, funding rates, or market statistics.
---

# BingX Coin-M (CSwap) Market Data

Public market data for BingX Coin-M inverse perpetual futures. No HMAC signature required, but a `timestamp` query parameter is required for all endpoints.

Coin-M contracts are **coin-margined** (settled in the base asset, e.g., BTC). Symbol format is `BASE-USD` (e.g., `BTC-USD`, `ETH-USD`).

## Quick Reference

| Endpoint | Method | Description | Required | Optional | Authentication |
|----------|--------|-------------|----------|----------|----------------|
| `/openApi/cswap/v1/market/contracts` | GET | Contract specifications | None | None | No |
| `/openApi/cswap/v1/market/depth` | GET | Order book bids & asks | symbol | None | No |
| `/openApi/cswap/v1/market/klines` | GET | OHLCV candlestick data | symbol, interval | startTime, endTime, limit | No |
| `/openApi/cswap/v1/market/premiumIndex` | GET | Mark price & current funding rate | None | symbol | No |
| `/openApi/cswap/v1/market/openInterest` | GET | Total open interest | symbol | None | No |
| `/openApi/cswap/v1/market/ticker` | GET | 24h price change statistics | None | symbol | No |

---

## Parameters

### Common Parameters

* **symbol**: Trading pair in `BASE-USD` format (e.g., `BTC-USD`, `ETH-USD`). Note: Coin-M uses `USD`, not `USDT`.
* **limit**: Number of results to return. Default and max vary per endpoint.
* **startTime**: Start timestamp in milliseconds (e.g., `1735693200000`)
* **endTime**: End timestamp in milliseconds (e.g., `1735693200000`)
* **interval**: Kline/candlestick interval (see Enums below)

### Enums

* **interval**: `1m` | `3m` | `5m` | `15m` | `30m` | `1h` | `2h` | `4h` | `6h` | `12h` | `1d` | `3d` | `1w` | `1M`

### Parameter Validation Rules

* **symbol**: Must match `^[A-Z0-9]+-USD$`; max 20 characters (e.g., `BTC-USD`). Coin-M uses `USD`, not `USDT`
* **limit**: Positive integer; default and max vary per endpoint
* **startTime** / **endTime**: Unix timestamps in milliseconds; `endTime` must be ≥ `startTime`
* **interval**: Must exactly match one of the enum values above

---

## Quick Start

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md)

**TypeScript helper:**

```typescript
// Base URLs — see references/base-urls.md for all environments
const BASE_URLS = ["https://open-api.bingx.com", "https://open-api.bingx.pro"];

async function coinmMarket(
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

**24h ticker price for BTC-USD:**

```typescript
const ticker = await coinmMarket("/openApi/cswap/v1/market/ticker", {
  symbol: "BTC-USD",
});
// ticker.lastPrice, ticker.priceChangePercent, ticker.volume
```

**Order book depth for BTC-USD:**

```typescript
const depth = await coinmMarket("/openApi/cswap/v1/market/depth", {
  symbol: "BTC-USD",
});
// depth.bids: [price, qty][], depth.asks: [price, qty][]
```

**1-hour klines (last 100 candles):**

```typescript
const klines = await coinmMarket("/openApi/cswap/v1/market/klines", {
  symbol: "BTC-USD",
  interval: "1h",
  limit: 100,
});
// Each item: [openTime, open, high, low, close, volume, closeTime]
```

**Mark price & current funding rate:**

```typescript
const premium = await coinmMarket("/openApi/cswap/v1/market/premiumIndex", {
  symbol: "BTC-USD",
});
// premium.markPrice, premium.lastFundingRate, premium.nextFundingTime
```

**Open interest:**

```typescript
const oi = await coinmMarket("/openApi/cswap/v1/market/openInterest", {
  symbol: "BTC-USD",
});
// oi.openInterest, oi.symbol, oi.time
```

**All contract specifications:**

```typescript
const contracts = await coinmMarket("/openApi/cswap/v1/market/contracts");
// Array of contract objects: symbol, pricePrecision, minTickSize, minTradeValue, status
```

## Additional Resources

For complete parameter descriptions, optional fields, and full response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

cswap-market provides public read-only market data. No HMAC signature required (only `timestamp` parameter needed), **no CONFIRM needed**. The interaction goal is to collect query parameters.

> **Note**: Coin-M contract trading pair format is `BASE-USD` (e.g. `BTC-USD`), not `BASE-USDT`.

### Operation Identification

When the user's request is vague (e.g. "check Coin-M market" or "look at BTC inverse contract"), first identify what type of data they want to query:

> Please select the market data type:
> - Price / 24h change — ticker
> - Order book depth — depth
> - K-lines / Candlesticks — klines
> - Mark price / Funding rate — premiumIndex
> - Open interest — openInterest
> - Contract specification list — contracts

### When symbol is missing

Applicable endpoints: depth, klines, openInterest

> Please select a trading pair (or type another):
> - BTC-USD
> - ETH-USD
> - BNB-USD
> - Other (enter manually, format: BASE-USD)

If the trading pair can be inferred from context (e.g. "BTC K-lines today" or "Ethereum inverse contract funding rate"), infer it automatically without asking again.

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

### Endpoints where symbol is optional

symbol is optional for ticker and premiumIndex. If the user does not specify, query all contracts and inform the user; if a trading pair is specified, query only that pair.
