# BingX Spot WebSocket Market Data — API Reference

## Connection

**WebSocket URL:** `wss://open-api-ws.bingx.com/market`

- All messages are GZIP compressed; client must decompress before parsing
- Server sends ping messages; client must reply `Pong` to keep connection alive
- No authentication required for market data streams

---

## Subscription: Trade Detail

Subscribe to real-time trade detail data. Due to multi-threaded push, trade IDs may not be strictly ordered.

### dataType Format

`{symbol}@trade`

Example: `BTC-USDT@trade`

### Subscription Request

```json
{
  "id": "24dd0e35-56a4-4f7a-af8a-394c7060909c",
  "reqType": "sub",
  "dataType": "BTC-USDT@trade"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
| dataType | string | Yes | Symbol must contain `-` |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USDT@trade` |
| data | Array of trade records |
| data[].T | Trade time (ms) |
| data[].s | Symbol |
| data[].p | Price |
| data[].q | Quantity |
| data[].m | Is buyer maker |

---

## Subscription: K-Line Streams

Subscribe to candlestick/kline data.

### dataType Format

`{symbol}@kline_{interval}`

Example: `BTC-USDT@kline_1min`

### Supported Intervals

`1min`, `3min`, `5min`, `15min`, `30min`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`

> **Note**: Spot uses `min` suffix (e.g., `1min`), unlike swap which uses `m` (e.g., `1m`).

### Subscription Request

```json
{
  "id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40",
  "reqType": "sub",
  "dataType": "BTC-USDT@kline_1min"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
| dataType | string | Yes | Symbol must contain `-`. K-line interval type (see Supported Intervals above) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USDT@kline_1min` |
| data.s | Symbol |
| data.K.t | Kline start time |
| data.K.T | Kline close time |
| data.K.o | Open |
| data.K.h | High |
| data.K.l | Low |
| data.K.c | Close |
| data.K.v | Volume |

---

## Subscription: Market Depth

Push limited depth information every 300ms. Default level 20.

### dataType Format

`{symbol}@depth{level}`

Example: `BTC-USDT@depth50`

### Supported Levels

`5`, `10`, `20`, `50`, `100`

### Subscription Request

```json
{
  "id": "975f7385-7f28-4ef1-93af-df01cb9ebb53",
  "reqType": "sub",
  "dataType": "BTC-USDT@depth50"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
| dataType | string | Yes | Symbol must contain `-`. Depth level: 5, 10, 20, 50, 100 |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USDT@depth50` |
| data.bids | `[[price, qty], ...]` sorted descending |
| data.asks | `[[price, qty], ...]` sorted ascending |
| data.T | Timestamp (ms) |

---

## Subscription: 24-Hour Price Change

Push every 1000ms.

### dataType Format

`{symbol}@ticker`

Example: `BTC-USDT@ticker`

### Subscription Request

```json
{
  "id": "975f7385-7f28-4ef1-93af-df01cb9ebb53",
  "reqType": "sub",
  "dataType": "BTC-USDT@ticker"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
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

## Subscription: Latest Trade Price

Real-time push.

### dataType Format

`{symbol}@lastPrice`

Example: `BTC-USDT@lastPrice`

### Subscription Request

```json
{
  "id": "975f7385-7f28-4ef1-93af-df01cb9ebb53",
  "reqType": "sub",
  "dataType": "BTC-USDT@lastPrice"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
| dataType | string | Yes | Symbol must contain `-` (e.g., `BTC-USDT@lastPrice`) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USDT@lastPrice` |
| data.s | Symbol |
| data.c | Latest price |
| data.T | Timestamp (ms) |

---

## Subscription: Best Order Book (Book Ticker)

Real-time push.

### dataType Format

`{symbol}@bookTicker`

Example: `BTC-USDT@bookTicker`

### Subscription Request

```json
{
  "id": "975f7385-7f28-4ef1-93af-df01cb9ebb53",
  "reqType": "sub",
  "dataType": "BTC-USDT@bookTicker"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
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

## Subscription: Incremental and Full Depth

Push incremental depth of 1000 levels every 500ms.

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
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
| dataType | string | Yes | Symbol must contain `-` (e.g., `BTC-USDT@incrDepth`) |

### How to Maintain Incremental Depth Locally

1. First message: `action: "all"` — full snapshot with `lastUpdateId`
2. Subsequent: `action: "update"` — incremental. Nth update's `lastUpdateId` = (N-1)th + 1
3. If not continuous: reconnect or cache last 3 and try merge
4. Compare with local depth: Add / Remove (qty=0) / Update
5. Update cache and `lastUpdateId`

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USDT@incrDepth` |
| data.action | `all` or `update` |
| data.lastUpdateId | Sequence ID |
| data.bids | `[[price, qty], ...]` |
| data.asks | `[[price, qty], ...]` |
| data.T | Timestamp (ms) |

---

## Error Codes

WebSocket connections may encounter connection-level errors (network disconnects, heartbeat timeouts). For REST API error codes that may occur when querying market data via REST endpoints, see [Error Code Reference](../references/error-codes.md).
