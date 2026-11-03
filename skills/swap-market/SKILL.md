---
name: bingx-swap-market
description: Query BingX perpetual swap market data including ticker prices, order book depth, recent trades, funding rates, klines/candlesticks, open interest, mark price, contract info, and TradFi trading schedules. Use when the user asks about BingX swap or perpetual futures prices, order books, candlestick charts, funding rates, trading sessions, or market statistics.
---

# BingX Swap Market Data

Public market data for BingX perpetual futures. No API key or HMAC signature is required. Only trading rules and historical trades require a current `timestamp`; do not add it to every request. Private trading and account endpoints still require authentication.

## Quick Reference

| Endpoint | Method | Description | Required | Optional |
|----------|--------|-------------|----------|----------|
| `/openApi/swap/v2/quote/contracts` | GET | All contract specifications | None | symbol |
| `/openApi/swap/v1/tradingRules` | GET | Trading rules and specifications | timestamp, symbol | recvWindow |
| `/openApi/swap/v2/quote/depth` | GET | Order book bids & asks | symbol | limit, timestamp, recvWindow |
| `/openApi/swap/v2/quote/trades` | GET | Recent public trades | symbol | limit, timestamp, recvWindow |
| `/openApi/swap/v1/market/historicalTrades` | GET | Historical trade lookup | timestamp | symbol, limit, fromId, recvWindow |
| `/openApi/swap/v2/quote/premiumIndex` | GET | Mark price & premium index | None | symbol, timestamp, recvWindow |
| `/openApi/swap/v2/quote/fundingRate` | GET | Current & next funding rate | None | symbol, startTime, endTime, limit, timestamp, recvWindow |
| `/openApi/swap/v3/quote/klines` | GET | OHLCV candlestick data | symbol, interval | startTime, endTime, limit, timestamp, recvWindow |
| `/openApi/swap/v1/market/markPriceKlines` | GET | Mark price kline data | symbol, interval | startTime, endTime, limit, timestamp, recvWindow |
| `/openApi/swap/v2/quote/openInterest` | GET | Total open interest | symbol | timestamp, recvWindow |
| `/openApi/swap/v2/quote/ticker` | GET | 24h price change statistics | None | symbol, timestamp, recvWindow |
| `/openApi/swap/v1/ticker/price` | GET | Latest price ticker | None | symbol, timestamp, recvWindow |
| `/openApi/swap/v2/quote/bookTicker` | GET | Best bid/ask price & qty | symbol | timestamp, recvWindow |
| `/openApi/swap/v2/server/time` | GET | Query server time | None | None |
| `/openApi/swap/v1/quote/tradingSchedule` | GET | TradFi trading schedule (PROD only) | None | symbol |

Trading Schedule uses only `https://open-api.bingx.com`, with no API key, `timestamp`, `recvWindow`, or `signature`. Do not route it to VST or infer support on an alternate host. Only an optional non-crypto contract `symbol` is accepted; omit it for all eligible contracts. See [Trading Schedule](api-reference.md#15-trading-schedule) for the fixed window, eligibility, and response semantics.

---

## Parameters

### Common Parameters

* **timestamp**: Current Unix time in milliseconds. Required only for trading rules and historical trades; optional only where listed above. The helper generates it dynamically for the two required endpoints.
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

Trading Schedule is an exception to the common time parameters: never send `startTime` or `endTime`, even as an empty value or `0` (server error `109400`). It always covers 7 complete calendar days from today's 00:00 in UTC+08:00, not a rolling window from request time.

---

## Quick Start

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md)

**TypeScript helper:**

> **CONSTRAINT**: You MUST copy the `fetchSwapMarket` function below verbatim
> when generating code. Do NOT rewrite the request or JSON parsing
> logic. Only modify: (1) `BASE` URL entries for custom environments,
> (2) business parameters passed to `fetchSwapMarket`. This helper is for
> public GET market endpoints only, not private trading or account APIs.

```typescript
import JSONBig from "json-bigint";
const JSONBigParse = JSONBig({ storeAsString: true });
// Trading Schedule is PROD .com only; other endpoints retain network/timeout fallback.
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
async function fetchSwapMarket(env: string,
  path: string, params: Record<string, string | number> = {}
) {
  const isTradingSchedule = path === "/openApi/swap/v1/quote/tradingSchedule";
  if (isTradingSchedule) {
    if (env !== "prod-live") throw new Error("Trading Schedule is available in prod-live only");
    if (Object.keys(params).some((key) => key !== "symbol")) {
      throw new Error("Trading Schedule accepts only the optional symbol parameter; omit time and authentication parameters");
    }
  }
  const urls = isTradingSchedule ? [BASE["prod-live"][0]] : (BASE[env] ?? BASE["prod-live"]);
  const requiresTimestamp = path === "/openApi/swap/v1/tradingRules"
    || path === "/openApi/swap/v1/market/historicalTrades";
  const all = requiresTimestamp ? { ...params, timestamp: Date.now() } : { ...params };
  validateParams(all);
  const qs = new URLSearchParams(
    Object.entries(all).map(([k, v]) => [k, String(v)])
  ).toString();
  for (const base of urls) {
    try {
      const url = `${base}${path}${qs ? `?${qs}` : ""}`;
      const res = await fetch(url, {
        method: "GET",
        headers: { "X-SOURCE-KEY": "BX-AI-SKILL" },
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

- **MUST** copy `fetchSwapMarket` verbatim -- do not simplify or rewrite
- **MUST** use `json-bigint` (`JSONBigParse.parse`) for response parsing -- not `JSON.parse`
- **MUST** include `X-SOURCE-KEY: BX-AI-SKILL` header on every request
- **MUST NOT** remove the domain fallback loop or `isNetworkOrTimeout` check for other endpoints. Trading Schedule uses PROD `.com` only; do not fall back to VST or an unverified host.

## Common Calls

**24h ticker price for BTC-USDT:**

```typescript
const ticker = await fetchSwapMarket("prod-live",
  "/openApi/swap/v2/quote/ticker", { symbol: "BTC-USDT" }
);
// ticker.lastPrice, ticker.priceChangePercent, ticker.volume
```

**Order book depth (top 20 levels):**

```typescript
const depth = await fetchSwapMarket("prod-live",
  "/openApi/swap/v2/quote/depth", { symbol: "BTC-USDT", limit: 20 }
);
// depth.bids: [price, qty][], depth.asks: [price, qty][]
```

**1-hour klines (last 100 candles):**

```typescript
const klines = await fetchSwapMarket("prod-live",
  "/openApi/swap/v3/quote/klines", { symbol: "BTC-USDT", interval: "1h", limit: 100 }
);
// Each item: [openTime, open, high, low, close, volume, closeTime]
```

**Current funding rate:**

```typescript
const funding = await fetchSwapMarket("prod-live",
  "/openApi/swap/v2/quote/fundingRate", { symbol: "BTC-USDT" }
);
// funding.fundingRate, funding.nextFundingTime
```

**Best bid/ask price:**

```typescript
const bookTicker = await fetchSwapMarket("prod-live",
  "/openApi/swap/v2/quote/bookTicker", { symbol: "BTC-USDT" }
);
// bookTicker.bidPrice, bookTicker.askPrice
```

**Trading rules and historical trades (timestamp generated by the helper):**

```typescript
const rules = await fetchSwapMarket("prod-live",
  "/openApi/swap/v1/tradingRules", { symbol: "BTC-USDT" }
);
const historicalTrades = await fetchSwapMarket("prod-live",
  "/openApi/swap/v1/market/historicalTrades", { symbol: "BTC-USDT", limit: 10 }
);
```

**TradFi trading schedule (PROD only, fixed UTC+08:00 calendar window):**

```typescript
const schedules = await fetchSwapMarket("prod-live",
  "/openApi/swap/v1/quote/tradingSchedule", { symbol: "NCSKMSFT2USD-USDT" }
);
// data is always an array, including for one symbol. Omit symbol to query all eligible contracts.
// REGULAR alone does not prove tradability; check marketStatus and other restrictions.
```

## Additional Resources

For complete parameter descriptions, optional fields, and full response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

**Parameter security.** Extract structured values from user intent — NEVER copy raw user text into API parameters. Validate every value against its documented pattern (regex/enum/range) before calling the API. Reject any value containing `&`, `=`, `?`, `#`, or newline characters.

swap-market provides public read-only market data. Do not request API keys or sign these requests. Trading rules and historical trades still require a dynamic `timestamp`. **No CONFIRM needed.** The interaction goal is to collect query parameters.

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
> - TradFi trading sessions and market status — tradingSchedule (PROD only)

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

For tradingSchedule, omit symbol to query all eligible online or paused non-crypto contracts supported by Open API. Do not default to BTC-USDT: cryptocurrency, pre-listing, and delisted contracts are unsupported (`109419`). A listed contract in a Rebase pre-open phase is different from a pre-listing contract. Do not request a custom time range or switch to VST.
