# BingX Sub-Account Management — API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

**Common parameters** (apply to all endpoints below):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | int64 | Yes | Request timestamp in milliseconds |
| recvWindow | int64 | No | Request validity window in ms, max 5000 |

> **Body type note:** Endpoints marked **JSON** must be called with `Content-Type: application/json` and the params (including `signature`) sent as a JSON object in the request body. All other POST endpoints use `application/x-www-form-urlencoded`.

---

## 1. Account Identity

### 1.1 Query Account UID

`GET /openApi/account/v1/uid`

Rate limit: 10/s per UID. API Key permission: **Read**.

**Parameters:** No endpoint-specific parameters.

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `uid` | string | Account UID |

---

### 1.2 Query API Key Permissions

`GET /openApi/v1/account/apiPermissions`

Rate limit: 2/s per UID. API Key permission: **Read**.

**Parameters:** No endpoint-specific parameters.

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `ipRestrict` | bool | Whether IP restriction is enabled |
| `createTime` | long | API Key creation timestamp (ms) |
| `enableReading` | bool | Read permission enabled |
| `enableSpotAndMarginTrading` | bool | Spot & margin trading permission |
| `enableWithdrawals` | bool | Withdrawal permission |
| `enableInternalTransfer` | bool | Internal transfer permission |
| `enableFutures` | bool | Futures trading permission |
| `permitsUniversalTransfer` | bool | Universal transfer permission |
| `enableVanillaOptions` | bool | Options trading permission |

---

### 1.3 Query API Key Restrictions

`GET /openApi/v1/account/apiPermissions`

Rate limit: 2/s per UID. API Key permission: **Read**.

**Parameters:** No endpoint-specific parameters.

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `ipRestrict` | bool | Whether IP whitelist is enabled |
| `createTime` | long | API Key creation timestamp (ms) |
| `enableReading` | bool | Read permission |
| `enableSpotAndMarginTrading` | bool | Spot trading permission |
| `enableWithdrawals` | bool | Withdrawal permission |
| `enableInternalTransfer` | bool | Internal transfer permission |
| `enableFutures` | bool | Futures trading permission |
| `permitsUniversalTransfer` | bool | Universal transfer permission |

---

### 1.4 Query API Key Info

`GET /openApi/account/v1/apiKey/query`

Rate limit: 5/s per UID. API Key permission: **Read**.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `uid` | long | Yes | User UID (master or sub-account) |
| `apiKey` | string | No | Filter by specific API Key |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `apiKeyList` | array | List of API Key objects |
| `apiKeyList[].apiKey` | string | Masked API Key |
| `apiKeyList[].note` | string | Remark/label |
| `apiKeyList[].permissions` | array | Permission integers assigned |
| `apiKeyList[].ipAddresses` | array | IP whitelist |
| `apiKeyList[].createTime` | long | Creation timestamp (ms) |

---

## 2. Sub-account Lifecycle

### 2.1 Create Sub-account

`POST /openApi/subAccount/v1/create` — **JSON body**

Rate limit: 1/s per UID. API Key permission: **Manage Subaccounts**.

**Parameters (JSON body):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subAccountString` | string | Yes | Username: starts with letter, contains number, >6 chars |
| `note` | string | No | Notes |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `subUid` | long | New sub-account UID |
| `subAccountString` | string | Sub-account username |
| `note` | string | Notes |

---

### 2.2 Get Sub-account List

`GET /openApi/subAccount/v1/list`

Rate limit: 1/s per UID. API Key permission: **Read**.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subUid` | long | No | Filter by sub-account UID |
| `subAccountString` | string | No | Filter by sub-account username |
| `isFeeze` | bool | No | Freeze or not |
| `page` | int | Yes | Page number, starting from 1 |
| `limit` | int | Yes | Page size, maximum 1000 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `subAccountList` | array | List of sub-account objects |
| `subAccountList[].uid` | long | Sub-account UID |
| `subAccountList[].subAccountString` | string | Sub-account username |
| `subAccountList[].note` | string | Notes |
| `subAccountList[].isFreeze` | bool | Whether the account is frozen |
| `subAccountList[].createTime` | long | Creation timestamp (ms) |
| `total` | int | Total count |

---

### 2.3 Query Sub-account Fund Assets

`GET /openApi/subAccount/v1/assets`

Rate limit: 5/s per UID. API Key permission: **Read**.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subUid` | long | Yes | Sub-account UID |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `balances` | array | List of asset balance objects |
| `balances[].asset` | string | Asset/currency name |
| `balances[].free` | string | Available balance |
| `balances[].locked` | string | Locked balance |

---

### 2.4 Freeze / Unfreeze Sub-account

`POST /openApi/subAccount/v1/updateStatus` — **JSON body**

Rate limit: 1/s per UID. API Key permission: **Manage Subaccounts**.

**Parameters (JSON body):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subUid` | long | Yes | Sub-account UID |
| `freeze` | bool | Yes | `true` to freeze, `false` to unfreeze |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `subUid` | long | Sub-account UID |
| `isFreeze` | bool | Current frozen status |

---

### 2.5 Batch Query Sub-account Asset Overview

`GET /openApi/subAccount/v1/allAccountBalance`

Rate limit: 5/s per UID. API Key permission: **Read**.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pageIndex` | int | Yes | Page number, must be > 0 |
| `pageSize` | int | Yes | Page size, must be > 0, maximum 10 |
| `subUid` | long | No | Filter by sub-account UID |
| `accountType` | string | No | Account type, if left blank, all assets of the account will be checked by default. spot: spot (fund account), stdFutures|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `list` | array | List of sub-account asset overview objects |
| `list[].subUid` | long | Sub-account UID |
| `list[].balances` | array | Asset balances per account type |
| `total` | int | Total count |

---

## 3. API Key Management

### 3.1 Create API Key for Sub-account

`POST /openApi/subAccount/v1/apiKey/create` — **JSON body**

Rate limit: 5/s per UID. API Key permission: **Manage Subaccounts**.

**Parameters (JSON body):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subUid` | long | Yes | Sub-account UID |
| `note` | string | Yes | notes |
| `permissions` | Array | Yes | Permission codes: 1=Spot, 2=Read, 3=Perp Futures, 4=Universal Transfer, 5=Withdraw, 7=Internal Transfer |
| `ipAddresses` | Array | No | IP whitelist |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `apiKey` | string | Created API Key |
| `secretKey` | string | Secret Key (shown only once) |
| `note` | string | Label/remark |
| `permissions` | array | Assigned permissions |
| `ipAddresses` | array | IP whitelist |

---

### 3.2 Edit Sub-account API Key

`POST /openApi/subAccount/v1/apiKey/edit` — **JSON body**

Rate limit: 5/s per UID. API Key permission: **Manage Subaccounts**.

**Parameters (JSON body):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subUid` | long | Yes | Sub-account UID |
| `apiKey` | string | Yes | API Key to edit |
| `note` | string | Yes | notes |
| `permissions` | Array | Yes | permissions，1-Spot Trading，2-Read，3-Perpetual Futures Trading，4-Universal Transfer，7-Allow internal transfer of sub acco|
| `ipAddresses` | Array | No | New IP whitelist |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `apiKey` | string | API Key (masked) |
| `note` | string | Updated label |
| `permissions` | array | Updated permissions |
| `ipAddresses` | array | Updated IP whitelist |

---

### 3.3 Delete Sub-account API Key

`POST /openApi/subAccount/v1/apiKey/del` — **JSON body**

Rate limit: 5/s per UID. API Key permission: **Manage Subaccounts**.

**Parameters (JSON body):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subUid` | long | Yes | Sub-account UID |
| `apiKey` | string | Yes | API Key to delete |

**Response `data`:**

Returns empty object `{}` on success.

---

## 4. Transfers & Deposits

### 4.1 Authorize Sub-account Internal Transfers

`POST /openApi/account/v1/innerTransfer/authorizeSubAccount`

Rate limit: 5/s per UID. API Key permission: **Manage Subaccounts**.

**Parameters (form):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subUids` | string | Yes | User uid list, comma separated |
| `transferable` | boolean | Yes | `true` to allow, `false` to prohibit |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `successList` | array | UIDs successfully updated |
| `failList` | array | UIDs that failed |

---

### 4.2 Sub-account Internal Transfer

`POST /openApi/wallets/v1/capital/subAccountInnerTransfer/apply`

Rate limit: 5/s per UID. API Key permission: **Universal Transfer** or **Internal Transfer**.

**Parameters (form):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | Yes | Currency name (e.g., `USDT`) |
| `userAccountType` | int | Yes | Recipient identifier type: 1=UID, 2=Phone, 3=Email |
| `userAccount` | string | Yes | Recipient (UID, phone number, or email) |
| `amount` | float64 | Yes | Transfer amount |
| `walletType` | int | Yes | Account type: 1=Fund, 2=Standard Futures, 3=Perp Futures |
| `callingCode` | string | No | Country code — required when `userAccountType=2` |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `tranId` | string | Transfer ID |

---

### 4.3 Get Sub-account Deposit Addresses

`GET /openApi/wallets/v1/capital/subAccount/deposit/address`

Rate limit: 5/s per UID. API Key permission: **Read**.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | Yes | Name of the transfer coin |
| `subUid` | long | Yes | Sub-account UID |
| `offset` | int | No | Starting record offset, default 0 |
| `limit` | int | No | Page size, default 100, maximum 1000 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `addressList` | array | List of deposit address objects |
| `addressList[].coin` | string | Currency name |
| `addressList[].network` | string | Network |
| `addressList[].address` | string | Deposit address |
| `addressList[].tag` | string | Memo/tag |
| `total` | int | Total count |

---

### 4.4 Get Sub-account Deposit Records

`GET /openApi/wallets/v1/capital/deposit/subHisrec`

Rate limit: 5/s per UID. API Key permission: **Read**.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | No | Currency name filter |
| `subUid` | long | No | Sub-user UID, when not filled, query the deposit records of all sub-accounts under the parent username |
| `txId` | string | No | Transaction ID filter |
| `status` | int | No | Status filter: 0=In progress, 1=Completed, 6=Chain uploaded |
| `startTime` | long | No | Start time (Unix ms) |
| `endTime` | long | No | End time (Unix ms) |
| `offset` | int | No | Starting record offset, default 0 |
| `limit` | int | No | Page size, default 100, maximum 1000 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `depositList` | array | List of deposit records |
| `depositList[].uid` | long | Sub-account UID |
| `depositList[].coin` | string | Currency |
| `depositList[].amount` | string | Deposit amount |
| `depositList[].network` | string | Network |
| `depositList[].status` | int | Status code |
| `depositList[].address` | string | Deposit address |
| `depositList[].txId` | string | On-chain transaction ID |
| `depositList[].insertTime` | long | Record creation timestamp (ms) |
| `depositList[].transferType` | int | Transfer type |
| `total` | int | Total count |

---

### 4.5 Query Sub-account Internal Transfer Records

`GET /openApi/wallets/v1/capital/subAccount/innerTransfer/records`

Rate limit: 5/s per UID. API Key permission: **Read**.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | Yes | Currency name |
| `transferClientId` | string | No | Client's self-defined internal transfer ID. When both platform ID and transferClientId are provided as input, the query |
| `startTime` | long | No | Start time (Unix ms) |
| `endTime` | long | No | End time (Unix ms) |
| `offset` | int | No | Starting record offset, default 0 |
| `limit` | int | No | Page size, default 100, maximum 1000 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `records` | array | List of internal transfer records |
| `records[].tranId` | string | Transfer ID |
| `records[].coin` | string | Currency |
| `records[].amount` | string | Transfer amount |
| `records[].fromUid` | long | Sender UID |
| `records[].toUid` | long | Receiver UID |
| `records[].status` | int | Transfer status |
| `records[].createTime` | long | Creation timestamp (ms) |
| `total` | int | Total count |

---

### 4.6 Query Sub-account Transfer History (Master Account Only)

`GET /openApi/account/transfer/v1/subAccount/asset/transferHistory`

Rate limit: 5/s per UID. API Key permission: **Read**.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `uid` | long | Yes | UID to query |
| `type` | ENUM | No | Transfer type filter |
| `tranId` | string | No | Transfer ID filter |
| `startTime` | long | No | Start time (Unix ms) |
| `endTime` | long | No | End time (Unix ms) |
| `pageId` | int | No | Current page, default 1 |
| `pagingSize` | int | No | Page size, default 10, maximum 100 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `rows` | array | List of transfer history records |
| `rows[].tranId` | string | Transfer ID |
| `rows[].asset` | string | Asset name |
| `rows[].amount` | string | Transfer amount |
| `rows[].type` | string | Transfer type |
| `rows[].status` | string | Status |
| `rows[].timestamp` | long | Transfer timestamp (ms) |
| `total` | int | Total count |

---

### 4.7 Query Transferable Amounts (Master Account Only)

`POST /openApi/account/transfer/v1/subAccount/transferAsset/supportCoins`

Rate limit: 5/s per UID. API Key permission: **Read**.

**Parameters (form):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fromUid` | long | Yes | Sender UID |
| `fromAccountType` | int | Yes | Sender account type: 1=Fund, 2=Standard Futures, 3=Perp Futures |
| `toUid` | long | Yes | Receiver UID |
| `toAccountType` | int | Yes | Receiver account type: 1=Fund, 2=Standard Futures, 3=Perp Futures |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `coinList` | array | List of transferable coin objects |
| `coinList[].coin` | string | Currency name |
| `coinList[].transferableAmount` | string | Maximum transferable amount |

---

### 4.8 Sub-account Asset Transfer (Master Account Only)

`POST /openApi/account/transfer/v1/subAccount/transferAsset`

Rate limit: 5/s per UID. API Key permission: **Universal Transfer**.

**Parameters (form):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `assetName` | string | Yes | Asset name (e.g., `USDT`) |
| `transferAmount` | DECIMAL | Yes | Transfer amount |
| `fromUid` | long | Yes | Sender UID |
| `fromType` | int | Yes | Sender account category: 1=Master, 2=Sub-account |
| `fromAccountType` | int | Yes | Sender account type: 1=Fund, 2=Standard Futures, 3=Perp Futures |
| `toUid` | long | Yes | Receiver UID |
| `toType` | int | Yes | Receiver account category: 1=Master, 2=Sub-account |
| `toAccountType` | int | Yes | Receiver account type: 1=Fund, 2=Standard Futures, 3=Perp Futures |
| `remark` | string | Yes | Transfer remark |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `tranId` | string | Transfer transaction ID |

---

## 5. Permissions & Addresses

### 5.1 Query API Key Permissions

`GET /openApi/v1/account/apiRestrictions`

Query the permissions and restrictions of the current API Key.

Rate limit: 5/s per UID. API Key permission: **Read**.

**Parameters:**

**Parameters:** No endpoint-specific parameters.

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `ipRestrict` | boolean | Whether IP access is restricted |
| `createTime` | long | API Key creation time |
| `permitsUniversalTransfer` | boolean | Whether universal transfer is authorized |
| `enableReading` | boolean | Read permission enabled |
| `enableFutures` | boolean | Swap trading permission enabled |
| `enableSpotAndMarginTrading` | boolean | Spot trading permission enabled |

---

### 5.2 Create Deposit Address for Sub-account

`POST /openApi/wallets/v1/capital/deposit/createSubAddress`

Create a deposit address for a sub-account on a specified network.

Rate limit: 5/s per UID. API Key permission: **Write**.

> Request body is sent as `application/json`.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin` | string | Yes | Currency name, e.g. USDT |
| `subUid` | long | Yes | Sub-account UID |
| `network` | string | Yes | Network name, e.g. TRC20 |
| `walletType` | int | Yes | Account type: `1` Fund Account; `2` Standard Futures; `3` Perpetual Futures; `15` Spot Account |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `address` | string | Deposit address |
| `addressTag` | string | Address tag/memo |
| `addressWithPrefix` | string | Deposit address with prefix |
| `coin` | string | Currency name |
| `network` | string | Network name |
| `status` | decimal | Address status: `0` activated, `1` pending, `2` not applied |
| `ts` | long | Creation timestamp (ms) |
| `walletType` | int | Account type |

---

## Appendix: Enum Reference

### API Key Permissions

| Code | Description |
|------|-------------|
| `1` | Spot Trading |
| `2` | Read |
| `3` | Perpetual Futures Trading |
| `4` | Universal Transfer |
| `5` | Withdraw |
| `7` | Allow internal transfer of sub-accounts |

### Account Type Codes

| Code | Description |
|------|-------------|
| `1` | Fund Account |
| `2` | Standard Futures Account |
| `3` | Perpetual Futures Account (USDⓢ-M) |

### Account Category (fromType / toType)

| Code | Description |
|------|-------------|
| `1` | Master account |
| `2` | Sub-account |

### Deposit Status

| Code | Description |
|------|-------------|
| `0` | In progress |
| `1` | Completed |
| `6` | Chain uploaded |