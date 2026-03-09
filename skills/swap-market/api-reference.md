# BingX Swap Market Data — API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

**Common parameters** (apply to all endpoints below):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | int64 | Yes | Request timestamp in milliseconds |
| recvWindow | int64 | No | Request validity window in ms, max 5000 |

Market data endpoints do not require special API key permissions.

---

## 1. Get Contract Info

`GET /openApi/swap/v2/quote/contracts`

Returns specifications for all available perpetual swap contracts.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. BTC-USDT; omit for all |

**Response `data` — array of contract objects:**

| Field | Type | Description |
|-------|------|-------------|
| `contractId` | string | Unique contract identifier |
| `symbol` | string | Trading pair, e.g. `BTC-USDT` |
| `size` | string | Contract size (value per contract) |
| `quantityPrecision` | integer | Decimal places for order quantity |
| `pricePrecision` | integer | Decimal places for price |
| `feeRate` | string | Base fee rate (deprecated, use `makerFeeRate`/`takerFeeRate`) |
| `makerFeeRate` | float | Maker fee rate, e.g. `0.0002` = 0.02% |
| `takerFeeRate` | float | Taker fee rate, e.g. `0.0005` = 0.05% |
| `tradeMinLimit` | integer | Deprecated, use `tradeMinQuantity` |
| `tradeMinQuantity` | float | Minimum order quantity (in base asset), e.g. `0.0001` |
| `tradeMinUSDT` | float | Minimum order value (in USDT), e.g. `2` |
| `maxLongLeverage` | integer | Maximum leverage for long positions, e.g. `125` |
| `maxShortLeverage` | integer | Maximum leverage for short positions, e.g. `125` |
| `currency` | string | Settlement currency, e.g. `USDT` |
| `asset` | string | Base asset, e.g. `BTC` |
| `status` | integer | `1` = active, `0` = inactive |
| `apiStateOpen` | string | API open position status: `"true"` or `"false"` |
| `apiStateClose` | string | API close position status: `"true"` or `"false"` |
| `brokerState` | string | Broker status: `"true"` or `"false"` |
| `launchTime` | integer | Launch time (ms timestamp) |
| `maintainTime` | integer | Maintenance time (ms timestamp, `0` = no maintenance) |
| `offTime` | integer | Offline time (ms timestamp, `0` = not offline) |

---

## 2. Order Book Depth

`GET /openApi/swap/v2/quote/depth`

Returns current order book bids and asks.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `limit` | integer | No | Default 20, optional value:[5, 10, 20, 50, 100, 500, 1000] |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `bids` | `[string, string][]` | `[price, quantity]` pairs, best bid first |
| `asks` | `[string, string][]` | `[price, quantity]` pairs, best ask first |
| `T` | integer | Timestamp (ms) |

---

## 3. Recent Trades

`GET /openApi/swap/v2/quote/trades`

Returns the most recent public trades.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `limit` | integer | No | Number of trades. Default `500`. Max `1000`. |

**Response `data` — array of trade objects:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Trade ID |
| `price` | string | Trade price |
| `qty` | string | Trade quantity |
| `quoteQty` | string | Quote asset quantity |
| `time` | integer | Trade timestamp (ms) |
| `buyerMaker` | boolean | `true` if buyer was the maker |

---

## 4. Mark Price & Premium Index

`GET /openApi/swap/v2/quote/premiumIndex`

Returns mark price, index price, and premium index. Omit `symbol` to get all contracts.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | No | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT |

**Response `data` (single or array):**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `markPrice` | string | Current mark price |
| `indexPrice` | string | Current index price |
| `lastFundingRate` | string | Last funding rate |
| `nextFundingTime` | integer | Next funding time (ms) |
| `time` | integer | Timestamp (ms) |

---

## 5. Funding Rate

`GET /openApi/swap/v2/quote/fundingRate`

Returns the current funding rate and next funding time.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. `BTC-USDT` |
| `startTime` | int64 | No | Start time in milliseconds |
| `endTime` | int64 | No | End time in milliseconds |
| `limit` | int32 | No | default: 100 maximum: 1000 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `fundingRate` | string | Current funding rate (e.g. `"0.0001"`) |
| `fundingTime` | integer | Current funding time (ms) |
| `nextFundingTime` | integer | Next funding settlement time (ms) |

---

## 6. Kline / Candlestick Data

`GET /openApi/swap/v3/quote/klines`

Returns OHLCV candlestick data.

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
| `[8]` | Number of trades |
| `[9]` | Taker buy base asset volume |
| `[10]` | Taker buy quote asset volume |

---

## 7. Open Interest

`GET /openApi/swap/v2/quote/openInterest`

Returns the total open interest for a contract.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `openInterest` | string | Total open interest (in base asset) |
| `symbol` | string | Trading pair |
| `time` | integer | Timestamp (ms) |

---

## 8. 24h Ticker Price Change Statistics

`GET /openApi/swap/v2/quote/ticker`

Returns 24-hour rolling window price statistics. Omit `symbol` to get all contracts.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | No | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT |

**Response `data` (single object or array):**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `priceChange` | string | Price change over 24h |
| `priceChangePercent` | string | Price change percentage over 24h |
| `lastPrice` | string | Latest trade price |
| `lastQty` | string | Quantity of last trade |
| `openPrice` | string | Opening price 24h ago |
| `highPrice` | string | Highest price in 24h |
| `lowPrice` | string | Lowest price in 24h |
| `volume` | string | Base asset volume in 24h |
| `quoteVolume` | string | Quote asset volume in 24h |
| `openTime` | integer | Start of 24h window (ms) |
| `closeTime` | integer | End of 24h window (ms) |
| `askPrice` | string | Current best ask price |
| `askQty` | string | Current best ask quantity |
| `bidPrice` | string | Current best bid price |
| `bidQty` | string | Current best bid quantity |

---

## 9. Best Bid/Ask Price (Book Ticker)

`GET /openApi/swap/v2/quote/bookTicker`

Returns the best (top-of-book) bid and ask price and quantity. Omit `symbol` to get all contracts.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT |

**Response `data` (single object or array):**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `bidPrice` | string | Best bid price |
| `bidQty` | string | Best bid quantity |
| `askPrice` | string | Best ask price |
| `askQty` | string | Best ask quantity |
| `time` | integer | Timestamp (ms) |

---

## 10. Historical Trades

`GET /openApi/swap/v1/market/historicalTrades`

Query historical transaction records for a trading pair.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. BTC-USDT |
| `fromId` | int64 | No | Starting trade ID. Default returns most recent records |
| `limit` | int | No | Number of results, default 50, max 100 |

**Response `data` (array):**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Transaction ID |
| `price` | string | Transaction price |
| `qty` | string | Transaction quantity |
| `quoteQty` | string | Turnover |
| `time` | int64 | Transaction time (ms) |
| `isBuyerMaker` | bool | Whether the buyer is the maker |

---

## 11. Mark Price Kline/Candlestick Data

`GET /openApi/swap/v1/market/markPriceKlines`

Query mark price kline/candlestick data.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. BTC-USDT |
| `interval` | string | Yes | time interval, refer to field description |
| `startTime` | int64 | No | Start time in milliseconds |
| `endTime` | int64 | No | End time in milliseconds |
| `limit` | int64 | No | Default 500, max 1440 |

**Response `data` (array):**

| Field | Type | Description |
|-------|------|-------------|
| `open` | float64 | Open price |
| `close` | float64 | Close price |
| `high` | float64 | High price |
| `low` | float64 | Low price |
| `volume` | float64 | Transaction volume |
| `time` | int64 | K-line timestamp (ms) |

---

## 12. Symbol Price Ticker

`GET /openApi/swap/v1/ticker/price`

Get the latest price for a symbol or all symbols.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | No | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT. If omitted, returns all symbols |

**Response `data` (single object or array):**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `price` | string | Latest price |
| `time` | int64 | Matching engine time (ms) |

---

## 13. Trading Rules

`GET /openApi/swap/v1/tradingRules`

Query trading rules and limits for a contract.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. BTC-USDT. Please use uppercase letters. If not provided, information for all trading pairs will be returned |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `minSizeCoin` | string | Minimum order quantity in coin |
| `minSizeUsd` | string | Minimum order amount in USDT |
| `maxNumOrder` | string | Maximum open orders for this contract |
| `protectionThreshold` | string | Spread protection threshold |
| `buyMaxPrice` | string | Upper limit ratio for limit buy price |
| `buyMinPrice` | string | Lower limit ratio for limit buy price |
| `sellMaxPrice` | string | Upper limit ratio for limit sell price |
| `sellMinPrice` | string | Lower limit ratio for limit sell price |
| `marketRatio` | string | Price tolerance ratio for market orders |

---

## 14. Get Server Time

`GET /openApi/swap/v2/server/time`

Get the server timestamp.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `serverTime` | int64 | Server time in milliseconds |

---
