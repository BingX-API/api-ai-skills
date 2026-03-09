# BingX Fund Account — API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

**Common parameters** (apply to all endpoints below):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | int64 | Yes | Request timestamp in milliseconds |
| recvWindow | int64 | No | Request validity window in ms, max 5000 |

---

## 1. Fund Account Balance

### Query Fund Account Assets

`GET /openApi/spot/v1/account/balance`

Returns all coin balances in the fund (spot) account.

**Parameters:**

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `balances` | array | List of asset balance objects |
| `balances[].asset` | string | Asset symbol (e.g., `USDT`, `BTC`) |
| `balances[].free` | string | Available (free) balance |
| `balances[].locked` | string | Locked balance (e.g., in open orders) |

**Example response:**
```json
{
  "code": 0,
  "msg": "",
  "debugMsg": "",
  "data": {
    "balances": [
      { "asset": "USDT", "free": "1000.00", "locked": "0.00" },
      { "asset": "BTC",  "free": "0.05",    "locked": "0.01" }
    ]
  }
}
```

---

## 2. Asset Overview (All Accounts)

### Query Asset Overview Across All Account Types

`GET /openApi/account/v1/allAccountBalance`

Returns the USDT-equivalent balance for each account type held by the user.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `accountType` | string | No | Filter by account type (see AccountType enum). Returns all if omitted. |

**AccountType enum values:**

| Value | Description |
|-------|-------------|
| `sopt` | Spot / Fund account |
| `stdFutures` | Standard futures account |
| `coinMPerp` | Coin-margined perpetual account |
| `USDTMPerp` | USDT-margined perpetual account |
| `copyTrading` | Copy trading account |
| `grid` | Grid trading account |
| `eran` | Wealth management account |
| `c2c` | C2C account |

**Response `data`:**

Array of account balance objects:

| Field | Type | Description |
|-------|------|-------------|
| `accountType` | string | Account type (see AccountType enum) |
| `usdtBalance` | string | Equivalent total balance in USDT |

**Example response:**
```json
{
  "code": 0,
  "timestamp": 1700000000000,
  "data": [
    { "accountType": "sopt",      "usdtBalance": "1000.00" },
    { "accountType": "USDTMPerp", "usdtBalance": "500.00"  }
  ]
}
```

---

## 3. Asset Transfer

### Transfer Assets Between Account Types

`POST /openApi/api/asset/v1/transfer`

Transfers an asset between the user's own accounts (e.g., Fund → Spot, Fund → Perpetual Futures).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fromAccount` | string | Yes | Source account (fund, spot, stdFutures, coinMPerp, USDTMPerp) |
| `toAccount` | string | Yes | Destination account (fund, spot, stdFutures, coinMPerp, USDTMPerp) |
| `asset` | string | Yes | Coin name (e.g., `USDT`, `BTC`) |
| `amount` | decimal | Yes | Transfer amount |

**Account Type Values:**

| Value | Description |
|-------|-------------|
| `fund` | Funding Account |
| `spot` | Spot Account |
| `stdFutures` | Standard Contract Account |
| `coinMPerp` | Coin-Margined Perpetual Account |
| `USDTMPerp` | USDT-Margined Perpetual Account |
| `PFUTURES_SFUTURES` | Perpetual Futures → Standard Contract |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `tranId` | string | Transaction ID of the completed transfer |

**Example response:**
```json
{
  "code": 0,
  "msg": "",
  "data": {
    "tranId": "8374927364827"
  }
}
```

---

## 4. Asset Transfer Records

### Query Asset Transfer Records

`GET /openApi/api/v3/asset/transfer`

Returns historical asset transfer records. Query by `type` or `tranId` (at least one required).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Conditional | Transfer direction (required if `tranId` not provided) |
| `tranId` | integer | Conditional | Transaction ID (required if `type` not provided) |
| `startTime` | integer | No | Start time in milliseconds |
| `endTime` | integer | No | End time in milliseconds |
| `current` | integer | No | Page index, default `1` |
| `size` | integer | No | Page size, default `10`, max `100` |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | integer | Total number of matching records |
| `rows` | array | List of transfer records |
| `rows[].asset` | string | Coin name |
| `rows[].amount` | string | Transfer amount |
| `rows[].type` | string | Transfer direction |
| `rows[].status` | string | Transfer status (e.g., `CONFIRMED`) |
| `rows[].tranId` | integer | Transaction ID |
| `rows[].timestamp` | integer | Transfer timestamp in milliseconds |

**Example response:**
```json
{
  "code": 0,
  "msg": "",
  "data": {
    "total": 2,
    "rows": [
      {
        "asset": "USDT",
        "amount": "100.00",
        "type": "FUND_PFUTURES",
        "status": "CONFIRMED",
        "tranId": 8374927364827,
        "timestamp": 1700000000000
      }
    ]
  }
}
```

---

## 5. Main Account Internal Transfer

### Internal P2P Transfer to Another BingX User

`POST /openApi/wallets/v1/capital/innerTransfer/apply`

Transfers assets from the current account to another BingX user identified by UID, phone, or email.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | Yes | Coin name (e.g., `USDT`) |
| `userAccountType` | integer | Yes | Recipient identifier type: `1`=UID, `2`=Phone number, `3`=Email |
| `userAccount` | string | Yes | Recipient account value (UID / phone number / email) |
| `amount` | decimal | Yes | Transfer amount |
| `walletType` | integer | Yes | Source account: `1`=Fund account, `2`=Standard contract account |
| `callingCode` | string | Conditional | Phone calling code (required when `userAccountType=2`, e.g., `86`) |
| `transferClientId` | string | No | Custom client ID for idempotency (unique per transfer) |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Platform-assigned unique internal transfer record ID |

**Example response:**
```json
{
  "code": 0,
  "timestamp": 1700000000000,
  "data": {
    "id": "9182736450192"
  }
}
```

---

## 6. Main Account Internal Transfer Records

### Query Internal Transfer History

`GET /openApi/wallets/v1/capital/innerTransfer/records`

Returns the internal transfer history for a specific coin.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | Yes | Coin name (e.g., `USDT`) |
| `transferClientId` | string | No | Filter by custom client ID |
| `startTime` | integer | No | Start time in milliseconds |
| `endTime` | integer | No | End time in milliseconds |
| `offset` | integer | No | Starting record number, default `0` |
| `limit` | integer | No | Page size, default `100`, max `1000` |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | integer | Total number of records |
| `data` | array | List of internal transfer records |
| `data[].id` | integer | Internal transfer record ID |
| `data[].coin` | string | Coin name |
| `data[].receiver` | integer | Recipient's UID |
| `data[].amount` | decimal | Transfer amount |
| `data[].status` | integer | Status: `4`=Pending review, `5`=Failed, `6`=Completed |
| `data[].fromUid` | integer | Sender's account UID |
| `data[].recordType` | string | Record direction: `out`=transfer out, `in`=transfer in |

**Internal Transfer Status values:**

| Value | Description |
|-------|-------------|
| `4` | Pending review |
| `5` | Failed |
| `6` | Completed |

**Example response:**
```json
{
  "code": 0,
  "timestamp": 1700000000000,
  "data": {
    "total": 1,
    "data": [
      {
        "id": 9182736450192,
        "coin": "USDT",
        "receiver": 987654321,
        "amount": 50.0,
        "status": 6,
        "fromUid": 123456789,
        "recordType": "out"
      }
    ]
  }
}
```
