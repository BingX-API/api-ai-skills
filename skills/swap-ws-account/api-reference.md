# BingX Swap WebSocket Account Data — API Reference

## Connection

**WebSocket URL:** `wss://open-api-swap.bingx.com/swap-market?listenKey=<key>`

- All messages are GZIP compressed; client must decompress before parsing
- Server sends `Ping`; client must reply `Pong` to keep connection alive
- **No channel subscription needed** — all events are pushed automatically after connecting with listenKey
- Listen Key valid for 1 hour; extend every 30 minutes via PUT REST API

---

## Listen Key REST APIs

### Generate Listen Key

`POST /openApi/user/auth/userDataStream`

Rate limit: 2/s per UID

**Headers:**

| Header | Value | Required |
|--------|-------|----------|
| X-BX-APIKEY | Your API Key | Yes |
| X-SOURCE-KEY | BX-AI-SKILL | Yes |

**Response:**

```json
{
  "listenKey": "a8ea75681542e66f1a50a1616dd06ed77dab61baa0c296bca03a9b13ee5f2dd7"
}
```

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `listenKey` | string | Listen Key for WebSocket authentication |

### Extend Listen Key Validity

`PUT /openApi/user/auth/userDataStream`

Rate limit: 2/s per UID

Extends validity to 60 minutes from this call. Recommended: call every 30 minutes.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| listenKey | string | Yes | The listen key to extend |

**Response `data`:** Standard `{ code, msg }` envelope with empty `data`. HTTP status codes: `200` Success, `204` No request parameters, `404` listenKey does not exist.

### Delete Listen Key

`DELETE /openApi/user/auth/userDataStream`

Rate limit: 2/s per UID

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| listenKey | string | Yes | The listen key to delete |

**Response `data`:** Standard `{ code, msg }` envelope with empty `data`. HTTP status codes: `200` Success, `204` No request parameters, `404` listenKey does not exist.

---

## listenKey Expired Push

Pushed when the current connection's listenKey expires. After receiving this, reconnect with a new listenKey.

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| e | string | Event type: `listenKeyExpired` |
| E | number | Event time (ms) |
| listenKey | string | The expired listenKey |

### Example

```json
{
  "e": "listenKeyExpired",
  "E": 1676964520421,
  "listenKey": "53c1067059c5401e216ec0562f4e9741f49c3c18239a743653d844a50c4db6c0"
}
```

---

## Account Balance and Position Update (ACCOUNT_UPDATE)

Pushed when account information changes (balance, positions). Not pushed if order status change doesn't affect account/positions.

### Subscription

N/A — Auto-pushed after connecting with listenKey. No explicit subscription needed.

### Trigger Reasons (field `m`)

- `DEPOSIT` — Deposit
- `WITHDRAW` — Withdrawal
- `ORDER` — Order fill
- `FUNDING_FEE` — Funding fee

### FUNDING_FEE Special Rules

- **Isolated position**: Only pushes affected asset balance (B) and the specific position (P) where funding fee occurred
- **Cross position**: Only pushes affected asset balance (B), no position info (P)

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| e | string | `ACCOUNT_UPDATE` |
| E | number | Event time (ms) |
| T | number | Push timestamp (ms) |
| a.m | string | Trigger reason |
| a.B | array | Balance updates |
| a.B[].a | string | Asset name (e.g., `USDT`) |
| a.B[].wb | string | Wallet balance |
| a.B[].cw | string | Cross wallet balance |
| a.B[].bc | string | Balance change |
| a.P | array | Position updates |
| a.P[].s | string | Symbol |
| a.P[].pa | string | Position amount |
| a.P[].ep | string | Entry price |
| a.P[].up | string | Unrealized PnL |
| a.P[].mt | string | Margin type (`cross`/`isolated`) |
| a.P[].ps | string | Position side (`LONG`/`SHORT`/`BOTH`) |

---

## Order Update (ORDER_TRADE_UPDATE)

Pushed when an order is created, filled, or changes status.

### Subscription

N/A — Auto-pushed after connecting with listenKey. No explicit subscription needed.

### Order Direction

- `BUY` — Buy
- `SELL` — Sell

### Order Types

- `MARKET` — Market order
- `LIMIT` — Limit order
- `STOP` — Stop loss limit
- `STOP_MARKET` — Stop loss market
- `TAKE_PROFIT` — Take profit limit
- `TAKE_PROFIT_MARKET` — Take profit market
- `TRIGGER_LIMIT` — Trigger limit order
- `TRIGGER_MARKET` — Trigger market order
- `TRAILING_STOP_MARKET` — Trailing stop market
- `TRAILING_TP_SL` — Trailing TP/SL
- `LIQUIDATION` — Liquidation order

### Execution Types

- `NEW` — New order
- `TRADE` — Trade/fill
- `CANCELED` — Canceled
- `EXPIRED` — Expired
- `CALCULATED` — ADL or liquidation

### Order Status

- `NEW` — Active
- `PARTIALLY_FILLED` — Partially filled
- `FILLED` — Fully filled
- `CANCELED` — Canceled
- `EXPIRED` — Expired

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| e | string | `ORDER_TRADE_UPDATE` |
| E | number | Event time (ms) |
| T | number | Order update time (ms) |
| o.s | string | Symbol |
| o.c | string | Client order ID |
| o.S | string | Side (`BUY`/`SELL`) |
| o.o | string | Order type |
| o.q | string | Original quantity |
| o.p | string | Order price |
| o.ap | string | Average fill price |
| o.x | string | Execution type |
| o.X | string | Order status |
| o.i | number | Order ID |
| o.l | string | Last filled quantity |
| o.z | string | Cumulative filled quantity |
| o.L | string | Last fill price |
| o.n | string | Commission |
| o.N | string | Commission asset |
| o.T | number | Order trade time (ms) |
| o.ps | string | Position side |
| o.rp | string | Realized profit |

---

## Account Config Update (ACCOUNT_CONFIG_UPDATE)

Pushed when leverage or margin mode changes. Full data pushed once on connection, then every 5 seconds.

### Subscription

N/A — Auto-pushed after connecting with listenKey. No explicit subscription needed.

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| e | string | `ACCOUNT_CONFIG_UPDATE` |
| E | number | Event time (ms) |
| ac.s | string | Symbol |
| ac.l | number | Long position leverage |
| ac.S | number | Short position leverage |
| ac.mt | string | Margin type (`cross`/`isolated`) |

---

## Error Codes

WebSocket connections may encounter connection-level errors (network disconnects, heartbeat timeouts). For REST API error codes that may occur when managing Listen Keys via `/openApi/user/auth/userDataStream`, see [Error Code Reference](../references/error-codes.md).
