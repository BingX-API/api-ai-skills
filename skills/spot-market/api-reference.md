# BingX Spot Market Data — API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** None (public endpoints) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

**Common parameters** (apply to all endpoints below):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | int64 | Yes | Request timestamp in milliseconds |
| recvWindow | int64 | No | Request validity window in ms, max 5000 |

---

## 1. Get Spot Trading Symbols

`GET /openApi/spot/v1/common/symbols`

Returns specifications for all available spot trading pairs. Optionally filter by symbol.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. `BTC-USDT`. Omit for all symbols. |

**Response `data.symbols` — array of symbol objects:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair, e.g. `BTC-USDT` |
| `minQty` | float | Minimum order quantity (base asset) |
| `maxQty` | float | Maximum order quantity (base asset) |
| `minNotional` | float | Minimum order value (quote asset) |
| `maxNotional` | float | Maximum order value (quote asset) |
| `status` | integer | Symbol status: `1` = active, `0` = inactive |
| `tickSize` | float | Minimum price increment |
| `stepSize` | float | Minimum quantity increment |

---

## 2. Order Book Depth (v1)

`GET /openApi/spot/v1/market/depth`

Returns current order book bids and asks for a trading pair.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `limit` | integer | No | Number of levels. Default `20`. Max `1000`. |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `bids` | `[string, string][]` | `[price, quantity]` pairs, best bid first |
| `asks` | `[string, string][]` | `[price, quantity]` pairs, best ask first |
| `ts` | integer | Timestamp (ms) |

---

## 3. Order Book Aggregation (v2)

`GET /openApi/spot/v2/market/depth`

Returns an aggregated order book with configurable price precision. Note: this endpoint uses underscore symbol format (e.g. `BTC_USDT`).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair in underscore format, e.g. `BTC_USDT` |
| `depth` | integer | Yes | Number of depth levels to return |
| `type` | string | Yes | Precision type: `step0` (highest precision) through `step5` (lowest) |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `bids` | `[string, string][]` | `[price, quantity]` pairs, best bid first |
| `asks` | `[string, string][]` | `[price, quantity]` pairs, best ask first |
| `ts` | integer | Timestamp (ms) |

---

## 4. Recent Trades

`GET /openApi/spot/v1/market/trades`

Returns the most recent public trades for a symbol.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `limit` | integer | No | Number of trades. Default `100`. Max `500`. |

**Response `data` — array of trade objects:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Trade ID |
| `price` | float | Trade price |
| `qty` | float | Trade quantity (base asset) |
| `time` | integer | Trade timestamp (ms) |
| `buyerMaker` | boolean | `true` if the buyer was the maker |

---

## 5. Kline / Candlestick Data (v2)

`GET /openApi/spot/v2/market/kline`

Returns OHLCV candlestick data for a symbol.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `interval` | string | Yes | Candle interval. See values below. |
| `startTime` | integer | No | Start timestamp (ms). |
| `endTime` | integer | No | End timestamp (ms). |
| `limit` | integer | No | Number of candles. Default `500`. Max `1440`. |

**Valid `interval` values:**
`1m` `3m` `5m` `15m` `30m` `1h` `2h` `4h` `6h` `8h` `12h` `1d` `3d` `1w` `1M`

**Response `data` — array of candles (each candle is an array):**

| Index | Description |
|-------|-------------|
| `[0]` | Open time (ms) |
| `[1]` | Open price |
| `[2]` | High price |
| `[3]` | Low price |
| `[4]` | Close price |
| `[5]` | Volume (base asset) |
| `[6]` | Close time (ms) |
| `[7]` | Quote asset volume |

---

## 6. 24h Ticker Price Change Statistics

`GET /openApi/spot/v1/ticker/24hr`

Returns 24-hour rolling window price statistics. Omit `symbol` to get all trading pairs.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | No | Trading pair. Omit for all symbols. |

**Response `data` — array of ticker objects:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `openPrice` | string | Opening price 24h ago |
| `highPrice` | string | Highest price in 24h |
| `lowPrice` | string | Lowest price in 24h |
| `lastPrice` | string | Latest trade price |
| `volume` | string | Base asset volume in 24h |
| `quoteVolume` | string | Quote asset volume in 24h |
| `openTime` | integer | Start of 24h window (ms) |
| `closeTime` | integer | End of 24h window (ms) |
| `bidPrice` | float | Current best bid price |
| `bidQty` | float | Current best bid quantity |
| `askPrice` | float | Current best ask price |
| `askQty` | float | Current best ask quantity |
| `priceChangePercent` | string | Price change percentage over 24h |

---

## 7. Symbol Price Ticker

`GET /openApi/spot/v2/ticker/price`

Returns the latest price trades for a symbol.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |

**Response `data` — array of symbol objects, each containing:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `trades` | array | Array of trade items (see below) |

**Trade item fields:**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | integer | Trade timestamp (ms) |
| `tradeId` | string | Trade ID |
| `price` | string | Trade price |
| `amount` | string | Trade amount |
| `type` | integer | Trade type: `1` = buy, `2` = sell |
| `volume` | string | Trade volume |

---

## 8. Symbol Order Book Ticker (Best Bid/Ask)

`GET /openApi/spot/v1/ticker/bookTicker`

Returns the best (top-of-book) bid and ask price and quantity for a symbol.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |

**Response `data` — array of order book ticker objects:**

| Field | Type | Description |
|-------|------|-------------|
| `eventType` | string | Data type identifier |
| `time` | integer | Timestamp (ms) |
| `symbol` | string | Trading pair |
| `bidPrice` | string | Best bid price |
| `bidVolume` | string | Best bid quantity |
| `askPrice` | string | Best ask price |
| `askVolume` | string | Best ask quantity |

---

## 9. Historical Klines

`GET /openApi/market/his/v1/kline`

Returns historical candlestick data (can go further back than the standard kline endpoint).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `interval` | string | Yes | Candle interval. Same values as Klines (§5). |
| `startTime` | integer | No | Start timestamp (ms). |
| `endTime` | integer | No | End timestamp (ms). |
| `limit` | integer | No | Default value: 500 Maximum value: 500 |

**Response `data` — array of candles (same format as Klines §5):**

| Index | Description |
|-------|-------------|
| `[0]` | Open time (ms) |
| `[1]` | Open price |
| `[2]` | High price |
| `[3]` | Low price |
| `[4]` | Close price |
| `[5]` | Volume (base asset) |
| `[6]` | Close time (ms) |
| `[7]` | Quote asset volume |

---

## 10. Historical Trade Lookup

`GET /openApi/market/his/v1/trade`

Returns older historical public trades (further back than Recent Trades endpoint).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `limit` | integer | No | Number of trades. Default `100`. Max `500`. |
| `fromId` | string | No | The last recorded trade ID to fetch from. |

**Response `data` — array of historical trade objects:**

| Field | Type | Description |
|-------|------|-------------|
| `tid` | string | Trade ID |
| `t` | integer | Trade time (seconds) |
| `ms` | integer | Milliseconds component of trade time |
| `s` | string | Trading pair |
| `p` | float | Trade price |
| `v` | float | Trade volume |
