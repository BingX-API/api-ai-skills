# BingX Spot WebSocket Account Data — API Reference

## Connection

**WebSocket URL:** `wss://open-api-ws.bingx.com/market?listenKey=<key>`

- All messages are GZIP compressed; client must decompress before parsing
- Server sends ping messages; client must reply `Pong` to keep connection alive
- **Explicit channel subscription required** — send subscribe messages for each event type
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

## Subscription: Order Update (spot.executionReport)

Pushed when a spot order is created, partially filled, fully filled, or canceled.

### Subscription Request

```json
{
  "id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40",
  "reqType": "sub",
  "dataType": "spot.executionReport"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` to subscribe, `unsub` to unsubscribe |
| dataType | string | Yes | Fixed value: `spot.executionReport` |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| dataType | string | `spot.executionReport` |
| data.e | string | Event type |
| data.E | number | Event time (ms) |
| data.s | string | Symbol |
| data.S | string | Side (`BUY`/`SELL`) |
| data.o | string | Order type (`LIMIT`/`MARKET`) |
| data.q | string | Original quantity |
| data.p | string | Order price |
| data.x | string | Execution type (`NEW`/`TRADE`/`CANCELED`/`EXPIRED`) |
| data.X | string | Order status (`NEW`/`PARTIALLY_FILLED`/`FILLED`/`CANCELED`/`EXPIRED`) |
| data.i | number | Order ID |
| data.l | string | Last filled quantity |
| data.z | string | Cumulative filled quantity |
| data.L | string | Last fill price |
| data.n | string | Commission |
| data.N | string | Commission asset |
| data.T | number | Trade time (ms) |

---

## Subscription: Account Balance Update (ACCOUNT_UPDATE)

Pushed when account balance changes.

### Subscription Request

```json
{
  "id": "gdfg2311-d0f6-4a70-8d5a-043e4c741b40",
  "reqType": "sub",
  "dataType": "ACCOUNT_UPDATE"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Subscription ID |
| reqType | string | Yes | `sub` to subscribe, `unsub` to unsubscribe |
| dataType | string | Yes | Fixed value: `ACCOUNT_UPDATE` |

### Trigger Reasons (field `m`)

- `DEPOSIT` — Deposit
- `WITHDRAW` — Withdrawal
- `ORDER` — Order fill
- `FUNDING_FEE` — Funding fee
- `WITHDRAW_REJECT` — Withdrawal rejected
- `ADJUSTMENT` — Adjustment
- `INSURANCE_CLEAR` — Insurance clear
- `ADMIN_DEPOSIT` — Admin deposit
- `ADMIN_WITHDRAW` — Admin withdrawal
- `MARGIN_TRANSFER` — Margin transfer
- `MARGIN_TYPE_CHANGE` — Margin type change
- `ASSET_TRANSFER` — Asset transfer
- `AUTO_EXCHANGE` — Auto exchange

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| e | string | Event type: `ACCOUNT_UPDATE` |
| E | number | Event time (ms) |
| T | number | Matching time (ms) |
| a.m | string | Trigger reason |
| a.B | array | Balance updates |
| a.B[].a | string | Asset name (e.g., `USDT`, `BTC`) |
| a.B[].wb | string | Wallet balance |
| a.B[].cw | string | Cross wallet balance |
| a.B[].bc | string | Balance change |

---

## Error Codes

WebSocket connections may encounter connection-level errors (network disconnects, heartbeat timeouts). For REST API error codes that may occur when managing Listen Keys via `/openApi/user/auth/userDataStream`, see [Error Code Reference](../references/error-codes.md).
