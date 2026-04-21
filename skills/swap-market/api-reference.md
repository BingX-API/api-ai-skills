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

Rate limit: 1/s per IP.

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

Rate limit: 1/s per IP.

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

Rate limit: 1/s per IP.

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

Rate limit: 1/s per IP.

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

Rate limit: 1/s per IP.

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

Rate limit: 1/s per IP.

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

Rate limit: 1/s per IP.

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

Rate limit: 1/s per IP.

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

Rate limit: 1/s per IP.

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

Rate limit: 1/s per IP.

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

Rate limit: 1/s per IP.

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

Rate limit: 1/s per IP.

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

Rate limit: 5/s per UID.

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

Rate limit: see [`references/rate-limits.md`](../references/rate-limits.md) for global policy (per-UID + per-IP throttling, 100410 backoff).

Get the server timestamp.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `serverTime` | int64 | Server time in milliseconds |

---

## Common Error Codes

Common gateway error codes applicable to all endpoints:

| Code | Description |
|------|-------------|
| `100001` | Request signature verification failed. Verify the signature algorithm, parameter order, and API secret. |
| `100004` | The API key does not have the required trading permission. Enable it in the API Key management page. |
| `100410` | Request rate limit exceeded. Reduce request frequency and retry after the cooldown period. |
| `100412` | Request is missing the signature parameter. Include a valid signature in your request. |
| `100413` | API Key is incorrect or missing. Ensure `X-BX-APIKEY` is set in the HTTP request header. |
| `100419` | The request IP is not in the API Key IP whitelist. Check IP whitelist settings. |
| `100421` | Null timestamp or timestamp mismatch with server time. Ensure your local clock is synchronized. |
| `100500` | System busy. Please retry later. |

Futures-specific error codes:

| Code | Description |
|------|-------------|
| `101204` | Insufficient margin to place the order. Add margin, lower leverage, or reduce order size. |
| `101206` | Account available balance is insufficient. Add funds and retry. |
| `101211` | Order price exceeds the allowed range (too high or too low). Adjust the price. |
| `101400` | Order parameter validation failed — amount below minimum, TP/SL price mismatch, duplicate clientOrderID, or pair suspended. |
| `101415` | This trading pair is suspended from opening positions or trading. Check announcements. |
| `101419` | Pending orders reached the upper limit. Cancel some pending orders first. |
| `101481` | The clientOrderID has already been used. Use a unique clientOrderID for each new order. |
| `104103` | Cannot switch position mode while positions or pending orders exist. Close all first. |
| `109400` | Invalid request parameters — symbol format, missing fields, value range, timestamp, or position mode mismatch. |
| `109421` | The specified order does not exist — may have been filled, cancelled, or order ID is incorrect. |
| `109425` | The trading pair does not exist or is not supported. Call /openApi/swap/v2/quote/contracts to verify. |
| `109500` | Internal server error. If it persists, retry later or contact support. |
| `110206` | TP/SL orders reached the maximum limit. Cancel some existing TP/SL orders first. |
| `110400` | The submitted order parameters do not meet the requirements. Verify price, quantity, etc. |
| `110500` | Order system busy. Please retry later. |

For the complete error code list, see [Error Code Reference](../references/error-codes.md).
