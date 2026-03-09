# BingX Standard Contract API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

**Common parameters** (apply to all endpoints below):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | int64 | Yes | Request timestamp in milliseconds |
| recvWindow | int64 | No | Request validity window in ms, max 5000 |

---

## 1. Query Positions

`GET /openApi/contract/v1/allPosition`

Query all current positions in the standard contract account. No request parameters required.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|

**Response `data` (array):**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair, e.g. BTC-USDT |
| `initialMargin` | number | Margin |
| `leverage` | number | Leverage |
| `unrealizedProfit` | number | Unrealized profit and loss |
| `isolated` | bool | `true` = isolated margin mode |
| `entryPrice` | number | Average entry price |
| `positionSide` | string | Position direction: `LONG` or `SHORT` |
| `positionAmt` | number | Position quantity |
| `currentPrice` | number | Current price |
| `time` | int64 | Opening time (ms) |

---

## 2. Query Historical Orders

`GET /openApi/contract/v1/allOrders`

Query historical orders for a standard contract trading pair.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. BTC-USDT |
| `orderId` | int64 | No | Order ID filter |
| `startTime` | int64 | No | Start time in milliseconds |
| `endTime` | int64 | No | End time in milliseconds |
| `limit` | int64 | No | quantity, optional |

**Response `data` (array):**

| Field | Type | Description |
|-------|------|-------------|
| `orderId` | number | System order ID |
| `symbol` | string | Trading pair |
| `positionSide` | string | Position direction: `LONG` or `SHORT` |
| `status` | string | Order status, e.g. `CLOSED` |
| `avgPrice` | number | Average fill price |
| `cumQuote` | number | Transaction amount |
| `executedQty` | number | Filled quantity |
| `margin` | number | Margin |
| `leverage` | number | Leverage |
| `isolated` | bool | `true` = isolated margin mode |
| `closePrice` | number | Closing price |
| `positionId` | int64 | Position ID |
| `time` | int64 | Order time (ms) |
| `updateTime` | int64 | Last update time (ms) |

---

## 3. Query Standard Contract Balance

`GET /openApi/contract/v1/balance`

Query the standard contract account balance. No request parameters required.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `asset` | string | Asset name |
| `balance` | string | Total balance |
| `crossWalletBalance` | string | Cross-margin wallet balance |
| `crossUnPnl` | string | Cross-margin unrealized PnL |
| `availableBalance` | string | Available balance for orders |
| `maxWithdrawAmount` | string | Maximum transferable amount |
| `marginAvailable` | bool | Whether it can be used as margin |
| `updateTime` | number | Last update timestamp |

---

## Common Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 0 | Success | Request succeeded |
| 100001 | Signature authentication failed | Check API key and secret |
| 100500 | Internal server error | Retry after a short delay |
| 80001 | Request failed | General failure, check parameters |
