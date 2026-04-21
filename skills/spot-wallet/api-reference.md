# BingX Spot Wallet — API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

**Common parameters** (apply to all endpoints below):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | int64 | Yes | Request timestamp in milliseconds |
| recvWindow | int64 | No | Request validity window in ms, max 5000 |

---

## 1. Deposit Records

### Query Deposit History

`GET /openApi/api/v3/capital/deposit/hisrec`

Rate limit: 10 requests/s per UID. API Key permission: **Read**.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | No | coin name |
| `status` | int | No | Deposit status filter: `0`=In progress, `1`=Not credited, `2`=Wrong amount, `6`=Chain confirmed |
| `startTime` | long | No | Start of query range in milliseconds (e.g., `1658748648396`) |
| `endTime` | long | No | End Time 1658748648396 |
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Page size, default `1000`, max `1000` |
| `txId` | long | No | Blockchain transaction ID to filter by |

> **Note:** This endpoint returns a bare JSON array directly, NOT wrapped in the standard `{ code, msg, data }` envelope.

**Response** (array of deposit records):

| Field | Type | Description |
|-------|------|-------------|
| `insertTime` | long | Deposit creation timestamp (milliseconds) |
| `amount` | string | Deposit amount |
| `coin` | string | Coin name |
| `network` | string | Network used for the deposit |
| `address` | string | Deposit address |
| `addressTag` | string | Memo/tag (if applicable) |
| `txId` | string | Blockchain transaction ID |
| `status` | int | Deposit status: `0`=In progress, `1`=Not credited, `2`=Wrong amount, `6`=Confirmed |
| `unlockConfirm` | string | Required confirmations to unlock the deposit |
| `confirmTimes` | string | Current confirmation count / required confirmations (e.g., `"3/12"`) |

---

## 2. Withdrawal Records

### Query Withdrawal History

`GET /openApi/api/v3/capital/withdraw/history`

Rate limit: 10 requests/s per UID. API Key permission: **Read**.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | No | Unique withdrawal record ID |
| `coin` | string | No | Coin name (e.g., `USDT`) |
| `withdrawOrderId` | string | No | Custom ID, if there is none, this field will not be returned,When both the platform ID and withdraw order ID are passed |
| `status` | int | No | Withdrawal status filter: `4`=Under review, `5`=Failed, `6`=Completed |
| `startTime` | long | No | Starting time1658748648396 |
| `endTime` | long | No | End Time 1658748648396 |
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Page size, default `1000`, max `1000` |
| `txId` | string | No | Blockchain transaction ID to filter by |

> **Note:** This endpoint returns a bare JSON array directly, NOT wrapped in the standard `{ code, msg, data }` envelope.

**Response** (array of withdrawal records):

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique withdrawal record ID |
| `amount` | string | Withdrawal amount |
| `transactionFee` | string | Network fee charged |
| `coin` | string | Coin name |
| `status` | int | Withdrawal status: `4`=Under review, `5`=Failed, `6`=Completed |
| `address` | string | Destination withdrawal address |
| `addressTag` | string | Memo/tag (if applicable) |
| `txId` | string | Blockchain transaction ID |
| `applyTime` | string | Withdrawal submission timestamp |
| `network` | string | Network used |
| `withdrawOrderId` | string | Custom withdrawal ID (if provided at submission) |
| `info` | string | Additional reason or info (e.g., rejection reason) |
| `confirmNo` | int | Number of blockchain confirmations |

---

## 3. Coin Config

### Query Currency Deposit and Withdrawal Data

`GET /openApi/wallets/v1/capital/config/getall`

Rate limit: 5 requests/s per UID. API Key permission: **Read**.
Returns supported networks, fees, deposit/withdrawal limits, and enable status for each coin.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | No | Coin identification |
| `displayName` | string | No | The platform displays the currency pair name for display only. Unlike coins, coins need to be used for withdrawal and re|

**Response `data`** (array of coin configs):

| Field | Type | Description |
|-------|------|-------------|
| `coin` | string | Coin identifier (e.g., `USDT`) |
| `name` | string | Full coin name (e.g., `TetherUS`) |
| `networkList` | array | List of supported networks for this coin |

**Each `networkList` item:**

| Field | Type | Description |
|-------|------|-------------|
| `network` | string | Network identifier (e.g., `BEP20`, `ERC20`, `TRC20`) |
| `name` | string | Network display name |
| `depositEnable` | bool | Whether deposit is enabled on this network |
| `withdrawEnable` | bool | Whether withdrawal is enabled on this network |
| `withdrawFee` | string | Fixed withdrawal fee on this network |
| `withdrawMin` | string | Minimum withdrawal amount |
| `withdrawMax` | string | Maximum withdrawal amount per transaction |
| `minConfirm` | int | Minimum blockchain confirmations required for deposit |
| `depositDesc` | string | Deposit instructions or notes |
| `withdrawDesc` | string | Withdrawal instructions or notes |
| `specialTips` | string | Special network tips or warnings |
| `isDefault` | bool | Whether this is the default network |
| `contractAddress` | string | Smart contract address for token (if applicable) |

---

## 4. Withdraw

### Initiate a Withdrawal

`POST /openApi/wallets/v1/capital/withdraw/apply`

Rate limit: 2 requests/s per UID. API Key permission: **Withdraw**.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | Yes | Coin name (e.g., `USDT`) |
| `network` | string | No | Network name (e.g., `BEP20`, `ERC20`). Uses the default network if omitted. |
| `address` | string | Yes | Destination withdrawal address |
| `addressTag` | string | No | Tag or memo, some currencies support tag or memo |
| `amount` | float64 | Yes | Withdrawal amount |
| `walletType` | int64 | Yes | Source account: `1`=Fund account, `2`=Standard contract, `3`=Perpetual futures |
| `withdrawOrderId` | string | No | Customer-defined withdrawal ID, a combination of numbers and letters, with a length of less than 100 characters |
| `vaspEntityId` | string | No | Payment platform information, only KYC=KOR (Korean individual users) must pass this field. List values Bithumb, Coinone,|
| `recipientLastName` | string | No | The recipient's surname is in English, and only KYC=KOR (Korean individual users) must pass this field. No need to fill |
| `recipientFirstName` | string | No | The recipient's name in English, only KYC=KOR (Korean individual users) must pass this field. No need to fill in when va|
| `dateOfbirth` | string | No | The payee's date of birth (example 1999-09-09) must be passed as this field only for KYC=KOR (Korean individual users). |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique withdrawal record ID assigned by BingX |

---

## 5. Deposit Address

### Query Main Account Deposit Address

`GET /openApi/wallets/v1/capital/deposit/address`

Rate limit: 2 requests/s per UID. API Key permission: **Read**.
Only available for main (mother) accounts.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | Yes | Name of the coin for transfer |
| `offset` | int | No | Starting record number, default `0` |
| `limit` | int | No | Page size, default `100`, max `1000` |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total number of deposit address records |
| `data` | array | Array of deposit address objects |

**Each address object:**

| Field | Type | Description |
|-------|------|-------------|
| `coin` | string | Coin name |
| `network` | string | Network identifier |
| `address` | string | Deposit address string |
| `tag` | string | Memo or tag (if applicable for this network) |
| `url` | string | Blockchain explorer URL for this address |

---

## 6. Deposit Risk Control Records

### Query Deposit Risk Control Records

`GET /openApi/wallets/v1/capital/deposit/riskRecords`

Rate limit: 2 requests/s per UID. API Key permission: **Read**.
Returns deposit records that are under risk control review for the main account and its sub-accounts.

**Parameters:**

No additional parameters required beyond common parameters.

**Response `data`** (array of risk-control deposit records):

| Field | Type | Description |
|-------|------|-------------|
| `insertTime` | long | Record creation timestamp (milliseconds) |
| `amount` | string | Deposit amount held under review |
| `coin` | string | Coin name |
| `network` | string | Network of the deposit |
| `address` | string | Deposit address |
| `txId` | string | Blockchain transaction ID |
| `status` | int | Risk control status code |
| `riskReason` | string | Reason the deposit was flagged for review |

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

Account / Wallet error codes:

| Code | Description |
|------|-------------|
| `100202` | Insufficient assets. Add funds and retry. |
| `100400` | Invalid request parameters — amount must be greater than 0, main account does not exist, or missing required parameter. |
| `100403` | The current account is not the main account. This endpoint is restricted to main accounts only. |
| `100437` | Coin does not exist or deposit address query failed. Verify the coin name. |
| `100450` | The current account information is incorrect (e.g. invalid sub-account UID). |

For the complete error code list, see [Error Code Reference](../references/error-codes.md).
