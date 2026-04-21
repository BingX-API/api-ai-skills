# BingX Spot Account — API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

**Common parameters** (apply to all endpoints below):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | int64 | Yes | Request timestamp in milliseconds |
| recvWindow | int64 | No | Request validity window in ms, max 5000 |

---

## Account and Assets

### 1. Query Spot Account Balance

`GET /openApi/spot/v1/account/balance`

Rate limit: 5/s per UID; 3/s per IP.

Query spot trading account assets and balances.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| *(none)* | | | |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `balances` | array | Asset list; see fields below |

**`balances` list entry fields:**

| Field | Type | Description |
|-------|------|-------------|
| `asset` | string | Asset symbol, e.g. `USDT`, `BTC` |
| `free` | string | Available balance |
| `locked` | string | Locked balance |

---

### 2. Query Fund Account Balance

`GET /openApi/fund/v1/account/balance`

Rate limit: 2/s per UID; 2/s per IP.

Query main account (fund account) balance.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `asset` | string | No | Coin name, return all when not transmitted |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `balance` | object | Account balance information |

---

### 3. Asset Overview (All Accounts)

`GET /openApi/account/v1/allAccountBalance`

Rate limit: 5/s per UID; 2/s per IP.

Query USDT-equivalent asset overview across all account types.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `accountType` | string | No | Account type; returns all if omitted. Options: `sopt`, `stdFutures`, `coinMPerp`, `USDTMPerp`, `copyTrading`, `grid`, `eran`, `c2c` |
| `recvWindow` | int | No | Request validity window (milliseconds) |

**Response `data` — Account asset list (array):**

| Field | Type | Description |
|-------|------|-------------|
| `accountType` | string | Account type |
| `usdtBalance` | string | USDT-equivalent value |

---

### 4. Transfer Assets Between Accounts

`POST /openApi/api/asset/v1/transfer`

Rate limit: 2/s per UID; 2/s per IP.

Transfer assets between different account types (e.g. spot ↔ perpetual futures).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `asset` | string | Yes | Asset name, e.g. `USDT` |
| `amount` | DECIMAL | Yes | Transfer amount |
| `fromAccount` | string | Yes | fromAccount, fund：Funding Account spot:Spot Account, stdFutures:Standard Contract, coinMPerp:COIN-M Perpetual Future, US|
| `toAccount` | string | Yes | toAccount, fund:Funding Account spot:Spot Account, stdFutures:Standard Contract, coinMPerp:COIN-M Perpetual Future, USDT|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `tranId` | string | Transfer record ID |

---

### 5. Query Asset Transfer Records (v3)

`GET /openApi/api/v3/asset/transfer`

Rate limit: 10/s per UID; 2/s per IP.

Query asset transfer history between accounts.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | ENUM | Yes | Transfer direction (at least one of `type` or `tranId` required) |
| `tranId` | int | No | transaction ID, (query by type or tranId) |
| `startTime` | int | No | Starting time1658748648396 |
| `endTime` | int | No | End time (milliseconds) |
| `current` | int | No | current page default1 |
| `size` | int | No | Page size default 10 can not exceed 100 |
| `recvWindow` | int | No | Request validity window (milliseconds), max 5000 |

> **Note:** This endpoint returns `{ total, rows }` directly at the top level, NOT wrapped in the standard `{ code, msg, data }` envelope.

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total record count |
| `rows` | array | Transfer record list |

**`rows` entry fields:**

| Field | Type | Description |
|-------|------|-------------|
| `asset` | string | Asset name |
| `amount` | string | Transfer amount |
| `type` | string | Transfer direction |
| `status` | string | Status: `CONFIRMED`, etc. |
| `tranId` | int | Transfer record ID |
| `timestamp` | int | Transfer timestamp (milliseconds) |

---

### 6. Query Asset Transfer Records (new format)

`GET /openApi/api/v3/asset/transferRecord`

Rate limit: 2/s per UID; 2/s per IP.

Query asset transfer records with enhanced filtering options.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fromAccount` | string | Yes* | fromAccount, fund：Funding Account spot:Spot Account, stdFutures:Standard Contract, coinMPerp:COIN-M Perpetual Future, US|
| `toAccount` | string | Yes* | toAccount, fund:Funding Account spot:Spot Account, stdFutures:Standard Contract, coinMPerp:COIN-M Perpetual Future, USDT|
| `transferId` | string | No | transaction ID, (query by fromAccount/toAccount or transferId). *Either both `fromAccount`+`toAccount` or `transferId` must be provided. |
| `pageIndex` | int | No | current page default1 |
| `pageSize` | int | No | Page size default 10 can not exceed 100 |
| `startTime` | int | No | Starting time1658748648396 |
| `endTime` | int | No | End time (milliseconds) |

> **Note:** This endpoint returns `{ total, rows }` directly at the top level, NOT wrapped in the standard `{ code, msg, data }` envelope.

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total record count |
| `rows` | array | Transfer record list |

**`rows` entry fields:**

| Field | Type | Description |
|-------|------|-------------|
| `transferId` | string | Transfer record ID |
| `asset` | string | Asset name |
| `amount` | string | Transfer amount |
| `fromAccount` | string | Source account (fund/spot/stdFutures/coinMPerp/USDTMPerp) |
| `toAccount` | string | Target account (fund/spot/stdFutures/coinMPerp/USDTMPerp) |
| `timestamp` | long | Transfer timestamp (milliseconds) |

---

### 7. Query Supported Coins for Transfer

`GET /openApi/api/asset/v1/transfer/supportCoins`

Rate limit: 2/s per UID; 2/s per IP.

Query the list of assets that support inter-account transfers.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fromAccount` | string | Yes | fromAccount, fund：Funding Account spot:Spot Account, stdFutures:Standard Contract, coinMPerp:COIN-M Perpetual Future, US|
| `toAccount` | string | Yes | toAccount, fund:Funding Account spot:Spot Account, stdFutures:Standard Contract, coinMPerp:COIN-M Perpetual Future, USDT|

**Response `data` — Array of supported coins:**

| Field | Type | Description |
|-------|------|-------------|
| `coin` | string | Coin symbol |
| `name` | string | Coin full name |

---

### 8. Internal P2P Transfer (Main Account)

`POST /openApi/wallets/v1/capital/innerTransfer/apply`

Rate limit: 2/s per UID; 2/s per IP.

Perform internal P2P transfer between main account and other accounts.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | Yes | Asset to transfer |
| `amount` | float | Yes | Transfer amount |
| `transferClientId` | string | No | Custom ID for internal transfer by the client, combination of numbers and letters, length less than 100 characters |
| `userAccountType` | int | Yes | Target user account type |
| `userAccount` | string | Yes | Target user account identifier |
| `callingCode` | string | No | Area code for telephone, required when userAccountType=2. |
| `walletType` | int | Yes | Account type, 1 Fund Account; 2 Standard Futures Account; 3 Perpetual Futures Account; 15 Spot Account |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Internal transfer ID |
| `transferClientId` | string | Client-defined transfer ID |

---

### 9. Query Internal Transfer Records

`GET /openApi/wallets/v1/capital/innerTransfer/records`

Rate limit: 10/s per UID; 2/s per IP.

Query main account internal P2P transfer history.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | Yes | Asset name |
| `id` | string | No | Transfer record ID filter |
| `transferClientId` | string | No | Client's self-defined internal transfer ID. When both platform ID and transferClientId are provided as input, the query |
| `startTime` | int | No | Start time (milliseconds) |
| `endTime` | int | No | End time (milliseconds) |
| `offset` | int | No | Starting offset, default 0 |
| `limit` | int | No | Items per page, default 100, max 1000 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Transfer record list |
| `total` | int | Total record count |

**Record entry fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Transfer ID |
| `coin` | string | Asset name |
| `receiver` | int | Recipient UID |
| `amount` | float | Transfer amount |
| `status` | int | Status: `4` pending, `5` failed, `6` completed |
| `fromUid` | int | Sender UID |
| `recordType` | string | `out` (outgoing) or `in` (incoming) |

---

*For full spot trading operations (place/cancel orders, OCO orders, etc.), see [spot-trade/SKILL.md](../spot-trade/SKILL.md).*

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
| `100500` | System busy or query failed. Please retry later. |

Spot-specific error codes:

| Code | Description |
|------|-------------|
| `100202` | Account balance is insufficient. Add funds and retry. |
| `100204` | Requested data not found — symbol does not exist, no data in queried time range, or time span too wide. |
| `100400` | Request parameter error or resource not found — missing required parameter, invalid symbol format, invalid interval, or order does not exist. |
| `100404` | Order does not exist. The order may have been filled or cancelled. |
| `100440` | Order price deviates too much from market price, triggering price protection. Adjust the price. |
| `100441` | Account is abnormal or advanced identity verification is required. Complete KYC or contact support. |
| `100490` | Spot trading pair is offline. Check status via /openApi/spot/v1/common/symbols. |

Rate limit: 1/s per IP.

| `101402` | This account does not support trading of this pair. Verify account permissions and pair status. |

For the complete error code list, see [Error Code Reference](../references/error-codes.md).
