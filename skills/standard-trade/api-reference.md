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

Rate limit: see [`references/rate-limits.md`](../references/rate-limits.md) for global policy (per-UID + per-IP throttling, 100410 backoff).

Query all current positions in the standard contract account. No request parameters required.

**Parameters:** No additional parameters beyond [common parameters](#common-parameters).

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

Rate limit: see [`references/rate-limits.md`](../references/rate-limits.md) for global policy (per-UID + per-IP throttling, 100410 backoff).

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

Rate limit: see [`references/rate-limits.md`](../references/rate-limits.md) for global policy (per-UID + per-IP throttling, 100410 backoff).

Query the standard contract account balance. No request parameters required.

**Parameters:** No additional parameters beyond [common parameters](#common-parameters).

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
| `109425` | The trading pair does not exist or is not supported. |
| `109500` | Internal server error. If it persists, retry later or contact support. |
| `110206` | TP/SL orders reached the maximum limit. Cancel some existing TP/SL orders first. |
| `110400` | The submitted order parameters do not meet the requirements. Verify price, quantity, etc. |
| `110500` | Order system busy. Please retry later. |

For the complete error code list, see [Error Code Reference](../references/error-codes.md).
