# BingX Coin-M (CSwap) Market Data — API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

**Common parameters** (apply to all endpoints below):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | int64 | Yes | Request timestamp in milliseconds |
| recvWindow | int64 | No | Request validity window in ms, max 5000 |

**Note:** Market data endpoints do not require HMAC; a `timestamp` query parameter is required for all endpoints.

**Symbol format:** `BASE-USD` (e.g., `BTC-USD`, `ETH-USD`) — coin-margined, **not** USDT-margined.

---

## 1. Contract Information

### Get Contract Specifications

`GET /openApi/cswap/v1/market/contracts`

Returns specifications for all available Coin-M perpetual contracts.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. `BTC-USD`; omit for all |

**Response `data`:** Array of contract objects.

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair, e.g. `BTC-USD` |
| `pricePrecision` | int | Decimal places for price |
| `minTickSize` | string | Minimum contract value (in USD) |
| `minTradeValue` | string | Minimum trade value (in USD) |
| `minQty` | string | Minimum order quantity (in contracts) |
| `status` | int | `1` = active |
| `timeOnline` | int64 | Contract listing timestamp (ms) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "timestamp": 1720074487610,
  "data": [
    {
      "symbol": "BTC-USD",
      "pricePrecision": 1,
      "minTickSize": "10",
      "minTradeValue": "10",
      "minQty": "1.00000000",
      "status": 1,
      "timeOnline": 1713175200000
    }
  ]
}
```

---

## 2. Order Book Depth

### Query Order Book

`GET /openApi/cswap/v1/market/depth`

Returns current bids and asks for a symbol.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USD` |
| `limit` | int64 | No | The number of returned results. The default is 20 if not filled, optional values: 5, 10, 20, 50, 100, 500, 1000. |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `bids` | array | Array of `[price, quantity]` pairs, best bid first |
| `asks` | array | Array of `[price, quantity]` pairs, best ask first |
| `ts` | int64 | Timestamp of the snapshot (ms) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "data": {
    "bids": [
      ["67500.0", "12"],
      ["67498.5", "5"]
    ],
    "asks": [
      ["67502.0", "8"],
      ["67504.0", "20"]
    ],
    "ts": 1720074487610
  }
}
```

---

## 3. K-line / Candlestick Data

### Get K-line Data

`GET /openApi/cswap/v1/market/klines`

Returns OHLCV candlestick data for a symbol.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USD` |
| `interval` | string | Yes | Time interval, optional values are: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M. |
| `startTime` | int64 | No | Start time, the returned result includes the K-line of this time. |
| `endTime` | int64 | No | End time, the returned result does not include the K-line of this time. |
| `limit` | int | No | Number of candles. Default: 500, max: 1440 |

**Interval Enum:**

`1m` `3m` `5m` `15m` `30m` `1h` `2h` `4h` `6h` `12h` `1d` `3d` `1w` `1M`

**Response `data`:** Array of candlestick arrays.

Each element: `[openTime, open, high, low, close, volume, closeTime]`

| Index | Field | Type | Description |
|-------|-------|------|-------------|
| 0 | `openTime` | int64 | Candle open timestamp (ms) |
| 1 | `open` | string | Open price |
| 2 | `high` | string | High price |
| 3 | `low` | string | Low price |
| 4 | `close` | string | Close price |
| 5 | `volume` | string | Base asset volume (in contracts) |
| 6 | `closeTime` | int64 | Candle close timestamp (ms) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "data": [
    [1720072800000, "67200.0", "67600.0", "67100.0", "67500.0", "1500", 1720076399999],
    [1720076400000, "67500.0", "67800.0", "67400.0", "67750.0", "1200", 1720079999999]
  ]
}
```

---

## 4. Mark Price & Current Funding Rate

### Get Mark Price and Funding Rate

`GET /openApi/cswap/v1/market/premiumIndex`

Returns the current mark price and funding rate. If `symbol` is omitted, returns data for all contracts.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. `BTC-USD`. Omit to get all. |

**Response `data`:** Single object (when symbol provided) or array (when omitted).

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `markPrice` | string | Current mark price |
| `indexPrice` | string | Current index price |
| `lastFundingRate` | string | Most recent funding rate (e.g., `"0.0001"` = 0.01%) |
| `nextFundingTime` | int64 | Next funding settlement timestamp (ms) |
| `time` | int64 | Data timestamp (ms) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "data": {
    "symbol": "BTC-USD",
    "markPrice": "67523.5",
    "indexPrice": "67510.0",
    "lastFundingRate": "0.0001",
    "nextFundingTime": 1720080000000,
    "time": 1720074487610
  }
}
```

---

## 5. Open Interest Statistics

### Get Open Interest

`GET /openApi/cswap/v1/market/openInterest`

Returns the total open interest for a symbol.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. `BTC-USD` |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `openInterest` | string | Total open interest (in contracts) |
| `time` | int64 | Data timestamp (ms) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "data": {
    "symbol": "BTC-USD",
    "openInterest": "52341",
    "time": 1720074487610
  }
}
```

---

## 6. 24hr Ticker Price Change Statistics

### Get 24h Ticker

`GET /openApi/cswap/v1/market/ticker`

Returns 24-hour rolling price change statistics. If `symbol` is omitted, returns data for all contracts.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. `BTC-USD`. Omit to get all. |

**Response `data`:** Single object (when symbol provided) or array (when omitted).

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `lastPrice` | string | Latest traded price |
| `openPrice` | string | Open price 24 hours ago |
| `highPrice` | string | 24h highest price |
| `lowPrice` | string | 24h lowest price |
| `volume` | string | 24h trading volume (in contracts) |
| `priceChange` | string | Absolute price change over 24h |
| `priceChangePercent` | string | Percentage price change over 24h |
| `time` | int64 | Data timestamp (ms) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "data": {
    "symbol": "BTC-USD",
    "lastPrice": "67523.5",
    "openPrice": "66800.0",
    "highPrice": "68100.0",
    "lowPrice": "66500.0",
    "volume": "98432",
    "priceChange": "723.5",
    "priceChangePercent": "1.083",
    "time": 1720074487610
  }
}
```

---

## Common Error Codes

| Code | Description |
|------|-------------|
| `0` | Success |
| `100400` | Invalid parameter |
| `100500` | Internal server error |
| `100503` | Server busy, retry later |
