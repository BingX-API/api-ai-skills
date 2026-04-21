# BingX Swap WebSocket Market Data — API Reference

## Connection

**WebSocket URL:** `wss://open-api-swap.bingx.com/swap-market`

- All messages are GZIP compressed; client must decompress before parsing
- Server sends `Ping`; client must reply `Pong` to keep connection alive
- No authentication required for market data streams

---

## Subscribe Market Depth Data

Push limited order book depth information.

### dataType Format

`{symbol}@depth{level}@{interval}`

Examples: `BTC-USDT@depth20@200ms`, `SOL-USDT@depth100@500ms`

BTC-USDT and ETH-USDT support 200ms push interval; other contracts use 500ms.

### Subscription Request

```json
{
  "id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40",
  "reqType": "sub",
  "dataType": "BTC-USDT@depth5@500ms"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID (UUID recommended) |
| reqType | string | Yes | `sub` to subscribe, `unsub` to unsubscribe |
| dataType | string | Yes | Symbol must contain `-`. Depth level: 5, 10, 20, 50, 100. Interval: 200ms, 500ms |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | Subscription channel identifier |
| data.bids | Bid side: `[[price, qty], ...]` sorted descending by price |
| data.asks | Ask side: `[[price, qty], ...]` sorted ascending by price |
| data.T | Timestamp (ms) |

---

## Subscribe the Latest Trade Detail

Real-time push of trade details.

### dataType Format

`{symbol}@trade`

Example: `BTC-USDT@trade`

### Subscription Request

```json
{
  "id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40",
  "reqType": "sub",
  "dataType": "BTC-USDT@trade"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID (UUID recommended) |
| reqType | string | Yes | `sub` to subscribe, `unsub` to unsubscribe |
| dataType | string | Yes | Symbol must contain `-` (e.g., `BTC-USDT@trade`) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USDT@trade` |
| data.T | Trade timestamp (ms) |
| data.s | Symbol |
| data.p | Trade price |
| data.q | Trade quantity |
| data.m | Is buyer the market maker |

---

## Subscribe K-Line Data

Subscribe to candlestick/kline data for a trading pair.

### dataType Format

`{symbol}@kline_{interval}`

Example: `BTC-USDT@kline_1m`

### Supported Intervals

`1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`

### Subscription Request

```json
{
  "id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40",
  "reqType": "sub",
  "dataType": "BTC-USDT@kline_1m"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID (UUID recommended) |
| reqType | string | Yes | `sub` to subscribe, `unsub` to unsubscribe |
| dataType | string | Yes | Symbol must contain `-`. K-line interval type (see Supported Intervals above) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USDT@kline_1m` |
| data.s | Symbol |
| data.K.t | Kline start time (ms) |
| data.K.T | Kline close time (ms) |
| data.K.o | Open price |
| data.K.h | High price |
| data.K.l | Low price |
| data.K.c | Close price |
| data.K.v | Volume |

---

## Subscribe to 24-Hour Price Changes

Push every 1 second.

### dataType Format

`{symbol}@ticker`

Example: `BTC-USDT@ticker`

### Subscription Request

```json
{
  "id": "24dd0e35-56a4-4f7a-af8a-394c7060909c",
  "reqType": "sub",
  "dataType": "BTC-USDT@ticker"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID (UUID recommended) |
| reqType | string | Yes | `sub` to subscribe, `unsub` to unsubscribe |
| dataType | string | Yes | Symbol must contain `-` (e.g., `BTC-USDT@ticker`) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USDT@ticker` |
| data.s | Symbol |
| data.c | Latest price |
| data.h | 24h high |
| data.l | 24h low |
| data.v | 24h volume |
| data.p | Price change |
| data.P | Price change percent |

---

## Subscribe to Latest Price Changes

Real-time push of latest trade price.

### dataType Format

`{symbol}@lastPrice`

Example: `BTC-USDT@lastPrice`

### Subscription Request

```json
{
  "id": "24dd0e35-56a4-4f7a-af8a-394c7060909c",
  "reqType": "sub",
  "dataType": "BTC-USDT@lastPrice"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID (UUID recommended) |
| reqType | string | Yes | `sub` to subscribe, `unsub` to unsubscribe |
| dataType | string | Yes | Symbol must contain `-` (e.g., `BTC-USDT@lastPrice`) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USDT@lastPrice` |
| data.s | Symbol |
| data.c | Latest price |
| data.T | Timestamp (ms) |

---

## Subscribe to Latest Mark Price Changes

Real-time push of mark price.

### dataType Format

`{symbol}@markPrice`

Example: `BTC-USDT@markPrice`

### Subscription Request

```json
{
  "id": "24dd0e35-56a4-4f7a-af8a-394c7060909c",
  "reqType": "sub",
  "dataType": "BTC-USDT@markPrice"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID (UUID recommended) |
| reqType | string | Yes | `sub` to subscribe, `unsub` to unsubscribe |
| dataType | string | Yes | Symbol must contain `-` (e.g., `BTC-USDT@markPrice`) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USDT@markPrice` |
| data.s | Symbol |
| data.p | Mark price |
| data.T | Timestamp (ms) |

---

## Subscribe to Book Ticker Streams

Push every 200ms. Best bid and ask price/quantity.

### dataType Format

`{symbol}@bookTicker`

Example: `BTC-USDT@bookTicker`

### Subscription Request

```json
{
  "id": "24dd0e35-56a4-4f7a-af8a-394c7060909c",
  "reqType": "sub",
  "dataType": "BTC-USDT@bookTicker"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID (UUID recommended) |
| reqType | string | Yes | `sub` to subscribe, `unsub` to unsubscribe |
| dataType | string | Yes | Symbol must contain `-` (e.g., `BTC-USDT@bookTicker`) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USDT@bookTicker` |
| data.s | Symbol |
| data.b | Best bid price |
| data.B | Best bid quantity |
| data.a | Best ask price |
| data.A | Best ask quantity |
| data.T | Timestamp (ms) |

---

## Incremental Depth Information

BTC-USDT and ETH-USDT push every 200ms; other trading pairs push every 800ms.

### dataType Format

`{symbol}@incrDepth`

Example: `BTC-USDT@incrDepth`

### Subscription Request

```json
{
  "id": "975f7385-7f28-4ef1-93af-df01cb9ebb53",
  "reqType": "sub",
  "dataType": "BTC-USDT@incrDepth"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID (UUID recommended) |
| reqType | string | Yes | `sub` to subscribe, `unsub` to unsubscribe |
| dataType | string | Yes | Symbol must contain `-` (e.g., `BTC-USDT@incrDepth`) |

### How to Maintain Incremental Depth Locally

1. After subscribing, first message has `action: "all"` — full depth snapshot with `lastUpdateId`
2. Subsequent messages have `action: "update"` — incremental updates. The Nth update's `lastUpdateId` should equal `(N-1)th lastUpdateId + 1`
3. If `lastUpdateId` is not continuous, reconnect or cache last 3 incremental updates and try to merge
4. For each incremental update, compare with local depth:
   - Price not in local depth → Add
   - Quantity is 0 → Remove
   - Quantity differs → Update
5. After traversal, update local depth cache and `lastUpdateId`

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USDT@incrDepth` |
| data.action | `all` (full snapshot) or `update` (incremental) |
| data.lastUpdateId | Sequence ID for continuity check |
| data.bids | `[[price, qty], ...]` |
| data.asks | `[[price, qty], ...]` |
| data.T | Timestamp (ms) |

---

## Error Codes

WebSocket connections may encounter connection-level errors (network disconnects, heartbeat timeouts). For REST API error codes that may occur when querying market data via REST endpoints, see [Error Code Reference](../references/error-codes.md).
