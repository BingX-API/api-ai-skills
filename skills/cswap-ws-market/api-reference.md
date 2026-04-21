# BingX Coin-M WebSocket Market Data — API Reference

## Connection

**WebSocket URL:** `wss://open-api-cswap-ws.bingx.com/market`

- All messages are GZIP compressed; client must decompress before parsing
- Server sends ping messages; client must reply `Pong` to keep connection alive
- No authentication required for market data streams
- **Symbol format:** `BTC-USD` (not `BTC-USDT`)

---

## Subscription: Trade Detail

Subscribe to real-time trade detail data.

### dataType Format

`{symbol}@trade`

Example: `BTC-USD@trade`

### Subscription Request

```json
{
  "id": "24dd0e35-56a4-4f7a-af8a-394c7060909c",
  "reqType": "sub",
  "dataType": "BTC-USD@trade"
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
| dataType | `BTC-USD@trade` |
| data | Array of trade records |
| data[].T | Trade time (ms) |
| data[].s | Symbol |
| data[].p | Price |
| data[].q | Quantity |
| data[].m | Is buyer maker |

---

## Subscription: Latest Trade Price

Real-time push of latest transaction price.

### dataType Format

`{symbol}@lastPrice`

Example: `BTC-USD@lastPrice`

### Subscription Request

```json
{
  "id": "24dd0e35-56a4-4f7a-af8a-394c7060909c",
  "reqType": "sub",
  "dataType": "BTC-USD@lastPrice"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
| dataType | string | Yes | Symbol must contain `-` (e.g., `BTC-USD@lastPrice`) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USD@lastPrice` |
| data.s | Symbol |
| data.c | Latest price |
| data.T | Timestamp (ms) |

---

## Subscription: Mark Price

Real-time push of mark price.

### dataType Format

`{symbol}@markPrice`

Example: `BTC-USD@markPrice`

### Subscription Request

```json
{
  "id": "24dd0e35-56a4-4f7a-af8a-394c7060909c",
  "reqType": "sub",
  "dataType": "BTC-USD@markPrice"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
| dataType | string | Yes | Symbol must contain `-` (e.g., `BTC-USD@markPrice`) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USD@markPrice` |
| data.s | Symbol |
| data.p | Mark price |
| data.T | Timestamp (ms) |

---

## Subscription: Limited Depth

Subscribe to limited order book depth.

### dataType Format

`{symbol}@depth{level}`

Example: `BTC-USD@depth5`

### Supported Levels

`5`, `10`, `20`, `50`, `100`

### Subscription Request

```json
{
  "id": "24dd0e35-56a4-4f7a-af8a-394c7060909c",
  "reqType": "sub",
  "dataType": "BTC-USD@depth5"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
| dataType | string | Yes | Symbol must contain `-`. Depth levels: 5, 10, 20, 50, 100 |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USD@depth5` |
| data.bids | `[[price, qty], ...]` sorted descending |
| data.asks | `[[price, qty], ...]` sorted ascending |
| data.T | Timestamp (ms) |

---

## Subscription: Best Bid and Ask (Book Ticker)

Real-time push.

### dataType Format

`{symbol}@bookTicker`

Example: `BTC-USD@bookTicker`

### Subscription Request

```json
{
  "id": "24dd0e35-56a4-4f7a-af8a-394c7060909c",
  "reqType": "sub",
  "dataType": "BTC-USD@bookTicker"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
| dataType | string | Yes | Symbol must contain `-` (e.g., `BTC-USD@bookTicker`) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USD@bookTicker` |
| data.s | Symbol |
| data.b | Best bid price |
| data.B | Best bid quantity |
| data.a | Best ask price |
| data.A | Best ask quantity |
| data.T | Timestamp (ms) |

---

## Subscription: K-Line Data

Subscribe to candlestick/kline data.

### dataType Format

`{symbol}@kline_{interval}`

Example: `BTC-USD@kline_1m`

### Supported Intervals

`1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`

### Subscription Request

```json
{
  "id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40",
  "reqType": "sub",
  "dataType": "BTC-USD@kline_1m"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
| dataType | string | Yes | Symbol must contain `-`. K-line interval (see Supported Intervals above) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USD@kline_1m` |
| data.s | Symbol |
| data.K.t | Kline start time |
| data.K.T | Kline close time |
| data.K.o | Open |
| data.K.h | High |
| data.K.l | Low |
| data.K.c | Close |
| data.K.v | Volume |

---

## Subscription: 24-Hour Price Change

Push every 1000ms.

### dataType Format

`{symbol}@ticker`

Example: `BTC-USD@ticker`

### Subscription Request

```json
{
  "id": "975f7385-7f28-4ef1-93af-df01cb9ebb53",
  "reqType": "sub",
  "dataType": "BTC-USD@ticker"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` / `unsub` |
| dataType | string | Yes | Symbol must contain `-` (e.g., `BTC-USD@ticker`) |

### Response Fields

| Field | Description |
|-------|-------------|
| dataType | `BTC-USD@ticker` |
| data.s | Symbol |
| data.c | Latest price |
| data.h | 24h high |
| data.l | 24h low |
| data.v | 24h volume |
| data.p | Price change |
| data.P | Price change percent |

---

## Error Codes

WebSocket connections may encounter connection-level errors (network disconnects, heartbeat timeouts). For REST API error codes that may occur when querying market data via REST endpoints, see [Error Code Reference](../references/error-codes.md).
