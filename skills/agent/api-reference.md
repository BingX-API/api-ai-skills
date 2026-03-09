# BingX Agent — API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

**Common parameters** (apply to all endpoints below):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | int64 | Yes | Request timestamp in milliseconds |
| recvWindow | int64 | No | Request validity window in ms, max 5000 |

---

## 1. Query Invited Users

### Endpoint

`GET /openApi/agent/v1/account/inviteAccountList`

Returns a paginated list of users invited by the current agent, with KYC, deposit, trade, and welfare status for each invitee.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pageIndex` | int | Yes | Page number, must be greater than 0 |
| `pageSize` | int | Yes | Page size, must be greater than 0 |
| `startTime` | long | No | Start timestamp in **milliseconds**. Maximum query window is 30 days. Omit together with `endTime` to query all data |
| `endTime` | long | No | End timestamp in **milliseconds**. Maximum query window is 30 days |
| `lastUid` | long | No | Required when queried data exceeds 10,000 records. Pass the last UID of the current page on each subsequent request; omit on the first request |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `list` | array | List of `InvitedUser` objects (see below) |
| `total` | int | Total number of invited users |
| `currentAgentUid` | long | Current agent UID |

**`InvitedUser` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `uid` | string | Invited user UID |
| `ownInviteCode` | string | Invitation code belonging to the invited user |
| `inviterSid` | long | Superior (parent agent) UID |
| `InvitationCode` | string | Invitation code used by the superior |
| `registerTime` | long | Registration timestamp in milliseconds |
| `directInvitation` | bool | `true` = direct invitation; `false` = indirect invitation |
| `kycResult` | string | `"true"` = KYC completed; `"false"` = KYC not completed |
| `deposit` | bool | `true` = has deposited; `false` = has not deposited |
| `balanceVolume` | string | Net assets in USDT |
| `trade` | bool | `true` = has traded (excludes trial/bonus fund trades); `false` = has not traded |
| `userLevel` | int | Customer level |
| `commissionRatio` | int | Commission percentage (unit: %) |
| `currentBenefit` | int | Welfare method: `0` = none, `1` = fee cashback, `2` = perpetual fee discount |
| `benefitRatio` | int | Transaction fee reduction percentage (unit: %) |
| `benefitExpiration` | long | Welfare expiration timestamp in milliseconds |

---

## 2. Daily Commission Details (Invitation Relationship)

### Endpoint

`GET /openApi/agent/v2/reward/commissionDataList`

Returns daily commission data per invited user broken down by business line (spot, perpetual swap, standard contract, copy trading, MT5).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `startTime` | date | Yes | Start date in days format (e.g. `"20240101"`). Maximum query window is 30 days. Sliding range of last 365 days |
| `endTime` | date | Yes | End date in days format (e.g. `"20240131"`). Maximum query window is 30 days |
| `pageIndex` | int | Yes | Page number, must be greater than 0 |
| `pageSize` | int | Yes | Page size, must be greater than 0 and maximum 100 |
| `uid` | long | No | Inquire about the daily commission of the user who invited the invitation by their UID. |
| `invitationCode` | string | No | Invitation code: Check the daily commissions of users associated with that invitation code. |
| `businessType` | string | No | perpetualFutures: Perpetual contracts; standardFutures: Standard contracts; spot: Spot trading; copyTradePro: External c|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `list` | array | List of `CommissionData` objects (see below) |
| `total` | int | Total number of records |
| `currentAgentUid` | long | Current agent UID |

**`CommissionData` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `uid` | long | Invited user UID |
| `commissionTime` | long | Commission date timestamp |
| `tradingVolume` | string | Total trading volume across all business lines, in USDT |
| `commissionVolume` | string | Total commission rebate amount in USDT |
| `spotTradingVolume` | string | Spot trading volume converted to USDT |
| `swapTradingVolume` | string | Perpetual contract trading volume converted to USDT |
| `stdTradingVolume` | string | Standard contract trading volume converted to USDT |
| `extCopyTradingVolume` | string | Copy trading volume converted to USDT |
| `mt5TradingVolume` | string | MT5 trading volume converted to USDT |
| `spotCommissionVolume` | string | Spot commission rebate amount in USDT |
| `swapCommissionVolume` | string | Perpetual contract commission rebate amount in USDT |
| `stdCommissionVolume` | string | Standard contract commission rebate amount in USDT |
| `extCopyCommissionVolume` | string | Copy trading commission rebate amount in USDT |
| `mt5CommissionVolume` | string | MT5 commission rebate amount in USDT |

---

## 3. Query Agent User Information

### Endpoint

`GET /openApi/agent/v1/account/inviteRelationCheck`

Looks up invitation relationship and account status for a specific user UID. Returns KYC, deposit, trade, welfare, and commission details.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `uid` | long | Yes | Invited user UID to query |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `uid` | long | Queried user UID |
| `existInviter` | string | `"true"` = has an inviter; `"false"` = no inviter |
| `inviteResult` | bool | `true` = invitation relationship exists; `false` = no invitation relationship |
| `directInvitation` | bool | `true` = direct invitation; `false` = indirect invitation |
| `inviterSid` | long | Superior (parent) UID |
| `registerDateTime` | long | Registration timestamp in milliseconds |
| `deposit` | bool | `true` = has deposited; `false` = has not deposited |
| `kycResult` | string | `"true"` = KYC completed; `"false"` = KYC not completed |
| `balanceVolume` | string | Net assets in USDT |
| `trade` | bool | `true` = has traded (excludes trial/bonus fund trades); `false` = has not traded |
| `userLevel` | int | Customer level |
| `commissionRatio` | int | Commission percentage (unit: %) |
| `currentBenefit` | int | Welfare method: `0` = none, `1` = fee cashback, `2` = perpetual fee discount |
| `benefitRatio` | int | Transaction fee reduction percentage (unit: %) |
| `benefitExpiration` | long | Welfare expiration timestamp in milliseconds |

---


## 4. Query API Transaction Commission (Non-Invitation Relationship)

### Endpoint

`GET /openApi/agent/v1/reward/third/commissionDataList`

Returns API trading commission data for users who are not under an invitation relationship with the agent. Only supports data after December 1, 2023.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `commissionBizType` | int | Yes | Commission business type: `81` = perpetual contract API commission; `82` = spot trading API commission |
| `startTime` | date | Yes | Start date in days format (e.g. `"20240101"`). Only supports data after 2023-12-01 |
| `endTime` | date | Yes | End date in days format (e.g. `"20240131"`). Only supports data after 2023-12-01 |
| `pageIndex` | int | Yes | Page number, must be greater than 0 |
| `pageSize` | int | Yes | Page size, must be greater than 0 and maximum 100 |
| `uid` | long | No | UID of the trading user (non-invitation relationship) |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `list` | array | List of `ApiTransactionCommissionData` objects (see below) |
| `total` | int | Total number of records |

**`ApiTransactionCommissionData` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `uid` | long | UID of the trading user (non-invitation relationship) |
| `commissionTime` | long | Commission date timestamp |
| `tradeVolume` | string | API order amount converted to USDT |
| `commissionVolume` | string | Rebate commission amount in USDT |
| `commissionBizType` | int | `81` = perpetual contract; `82` = spot |

---

## 5. Query Partner Information

### Endpoint

`GET /openApi/agent/v1/asset/partnerData`

Returns partner (sub-agent/broker) data including new referrals, first-time traders, deposit amounts, and commission ratios. Only supports querying the last 3 months.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `startTime` | long | Yes | Start timestamp in **days**. Only last 3 months supported |
| `endTime` | long | Yes | End timestamp in **days**. Only last 3 months supported |
| `pageIndex` | int | Yes | Page number, must be greater than 0 |
| `pageSize` | int | Yes | the maximum value is 200 |
| `uid` | long | No | Filter by a specific partner UID |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `list` | array | List of `PartnerInformationData` objects (see below) |
| `total` | int | Total number of records |

**`PartnerInformationData` object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `uid` | long | Partner UID |
| `email` | string | Partner email (encrypted/masked) |
| `Phone` | string | Partner phone number (encrypted/masked) |
| `referralType` | int | Invitation type: `1` = direct invitation; `2` = indirect invitation |
| `remarks` | string | Remarks/notes |
| `referrerUid` | long | Superior (parent) UID |
| `language` | string | Language preference |
| `newReferees` | string | Number of new invitees during the query period |
| `firstTrade` | string | Number of users who made their first trade during the query period |
| `branchDeposits` | string | Total channel deposit amount during the query period |
| `branchTrading` | string | Number of channel transactions during the query period |
| `branchTradingVol` | string | Total channel trading volume during the query period |
| `level` | string | Partner level |
| `commissionRatio` | string | Rebate/commission ratio |

---

## 6. Query Deposit Details of Invited Users

### Endpoint

`GET /openApi/agent/v1/asset/depositDetailList`

Query deposit details for users invited by the agent.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `uid` | long | Yes | Inviting user UID (must be the parent user UID) |
| `bizType` | int | Yes | Business type: `1` = Deposit |
| `startTime` | int64 | Yes | Start timestamp (days); only supports last 90 days |
| `endTime` | int64 | Yes | End timestamp (days); only supports last 90 days |
| `pageIndex` | int64 | Yes | Page number, must be > 0 |
| `pageSize` | int64 | Yes | Page size, must be > 0, max 100 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `list` | array | List of deposit detail objects |
| `total` | int | Total number of records |

**Deposit detail object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `uid` | long | Invited user UID |
| `inviteResult` | boolean | `true` = invitation relationship |
| `directInvitation` | boolean | `true` = direct invitation |
| `bizType` | int | `1` = Deposit |
| `bizTime` | long | Event time |
| `assetType` | int | Operation type breakdown |
| `assetTypeName` | string | Operation type name |
| `currencyName` | string | Currency |
| `currencyAmountVolume` | string | Amount |

---

## 7. Invitation Code Data

### Endpoint

`GET /openApi/agent/v1/commissionDataList/referralCode`

Query commission data grouped by invitation/referral code.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `referralCode` | string | No | Invitation code; omit to query all |
| `directInvitation` | string | Yes | `true` = direct invitation; `false` = indirect invitation |
| `startTime` | Long | No | Start time; supports last year; max query window 92 days; defaults to last 7 days if omitted |
| `endTime` | Long | No | End time only supports querying data for the most recent year. If neither startTime nor endTime is filled in, the defaul|
| `pageIndex` | int64 | No | Page number, default 1 |
| `pageSize` | int64 | No | Page size, default 100, max 200 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `list` | array | List of referral code commission objects |
| `total` | int | Total number of records |

**Referral code commission object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `referralCode` | string | Invitation code |
| `commissionRatio` | string | Commission percentage (%) |
| `friendEarn` | string | Friend cashback ratio (%) |
| `swapFeeDiscount` | string | Futures fee discount ratio (%) |
| `referralNum` | string | Number of invitees |
| `deposited` | string | Number of users who deposited |
| `traded` | string | Number of users who traded |
| `tradingVolume` | string | Transaction amount |
| `fee` | string | Fee |
| `offsetTradingFees` | string | Fee deduction |
| `payableTradingFees` | string | Actual transaction fee paid |
| `commission` | string | Your commission |

---

## 8. Superior Verification

### Endpoint

`GET /openApi/agent/v1/account/superiorCheck`

Verify whether a specified UID has an invitation (superior) relationship with the current agent.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `uid` | long | Yes | The account UID to check |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `inviteResult` | boolean | `true` = invitation relationship exists |
| `directInvitation` | boolean | `true` = direct invitation; `false` = indirect |

---

## Common Error Codes

| Code | Description |
|------|-------------|
| `0` | Success |
| `80001` | Authentication failed — check API key and signature |
| `80012` | Parameter error — check required fields and value ranges |
| `80014` | Timestamp error — ensure timestamp is within valid window |
| `100500` | Internal server error |

---

## Notes

- All authenticated endpoints require `X-BX-APIKEY` header and HMAC SHA256 `signature` parameter.
- `startTime`/`endTime` units differ by endpoint:
  - **Milliseconds**: `inviteAccountList`
  - **Days (date int/string)**: `commissionDataList`, `third/commissionDataList`, `partnerData`
- Pagination uses `pageIndex` (1-based) and `pageSize` for all endpoints.
- For `inviteAccountList` with >10,000 total records, use the `lastUid` cursor: pass the last UID from the current page in each subsequent request.