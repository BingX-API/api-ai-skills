# BingX Swap Account — API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

**Common parameters** (apply to all endpoints below):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | int64 | Yes | Request timestamp in milliseconds |
| recvWindow | int64 | No | Request validity window in ms, max 5000 |

---

## 1. Query Account Balance

`GET /openApi/swap/v3/user/balance`

Returns balance, equity, margin, and PnL summary for the perpetual futures account.

**Request Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|

**Response `data` — array of balance objects:**

| Field | Type | Description |
|-------|------|-------------|
| `userId` | string | User ID (partially masked) |
| `asset` | string | Settlement asset, e.g. `USDT` |
| `balance` | string | Total wallet balance |
| `equity` | string | Net equity (balance + unrealized PnL) |
| `unrealizedProfit` | string | Total unrealized profit and loss |
| `realisedProfit` | string | Total realized profit and loss |
| `availableMargin` | string | Available margin for new orders |
| `usedMargin` | string | Margin currently in use |
| `freezedMargin` | string | Frozen/reserved margin |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "data": [
    {
      "userId": "116***295",
      "asset": "USDT",
      "balance": "194.8212",
      "equity": "196.7431",
      "unrealizedProfit": "1.9219",
      "realisedProfit": "-109.2504",
      "availableMargin": "193.7609",
      "usedMargin": "1.0602",
      "freezedMargin": "0.0000"
    }
  ]
}
```

---

## 2. Query Position Data

`GET /openApi/swap/v2/user/positions`

Returns current open positions with PnL, liquidation price, leverage, and margin info.

**Request Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. `BTC-USDT`. Omit for all positions. |

**Response `data` — array of position objects:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair, e.g. `BTC-USDT` |
| `positionId` | string | Position ID |
| `positionSide` | string | Position direction: `LONG` or `SHORT` |
| `isolated` | bool | `true` = isolated margin mode; `false` = cross margin |
| `positionAmt` | string | Total position amount (in base asset) |
| `availableAmt` | string | Amount available to close |
| `unrealizedProfit` | string | Unrealized profit and loss |
| `realisedProfit` | string | Realized profit and loss |
| `initialMargin` | string | Initial margin used for this position |
| `liquidationPrice` | float64 | Estimated liquidation price |
| `avgPrice` | string | Average open price |
| `leverage` | int | Leverage multiplier |
| `positionValue` | string | Notional value of the position |
| `currency` | string | Settlement currency, e.g. `USDT` |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "data": [
    {
      "positionId": "1735*****52",
      "symbol": "BNB-USDT",
      "currency": "USDT",
      "positionAmt": "0.20",
      "availableAmt": "0.20",
      "positionSide": "SHORT",
      "isolated": true,
      "avgPrice": "246.43",
      "initialMargin": "9.7914",
      "leverage": 5,
      "unrealizedProfit": "-0.0653",
      "realisedProfit": "-0.0251",
      "liquidationPrice": 294.17
    }
  ]
}
```

---

## 3. Query User Commission Rate

`GET /openApi/swap/v2/user/commissionRate`

Returns the current user's taker and maker fee rates.

**Request Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|

**Response `data.commission`:**

| Field | Type | Description |
|-------|------|-------------|
| `takerCommissionRate` | float64 | Taker fee rate (e.g. `0.0005` = 0.05%) |
| `makerCommissionRate` | float64 | Maker fee rate (e.g. `0.0002` = 0.02%) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "data": {
    "commission": {
      "takerCommissionRate": 0.0005,
      "makerCommissionRate": 0.0002
    }
  }
}
```

---

## 4. Query Fund Flow (Income)

`GET /openApi/swap/v2/user/income`

Returns fund flow history for the perpetual futures account.

> - If neither `startTime` nor `endTime` is provided, only the **last 7 days** of data is returned.
> - If `incomeType` is not provided, all types are returned.
> - Only the **last 3 months** of data is retained.

**Request Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. `BTC-USDT` |
| `incomeType` | string | No | Fund flow type (see enum below) |
| `startTime` | int64 | No | Start time in milliseconds |
| `endTime` | int64 | No | End time in milliseconds |
| `limit` | int64 | No | Number of results. Default `100`, max `1000` |

**`incomeType` Enum:**

| Value | Description |
|-------|-------------|
| `TRANSFER` | Transfer |
| `REALIZED_PNL` | Realized profit and loss |
| `FUNDING_FEE` | Funding fee |
| `TRADING_FEE` | Trading fee |
| `INSURANCE_CLEAR` | Liquidation |
| `TRIAL_FUND` | Trial fund |
| `ADL` | Auto-deleveraging |
| `SYSTEM_DEDUCTION` | System deduction |
| `GTD_PRICE` | Guaranteed price |

**Response `data` — array of income records:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair, e.g. `BTC-USDT` |
| `incomeType` | string | Fund flow type |
| `income` | string | Amount. Positive = inflow, negative = outflow |
| `asset` | string | Asset, e.g. `USDT` |
| `info` | string | Remarks, varies by flow type |
| `time` | int64 | Timestamp in milliseconds |
| `tranId` | string | Transfer ID |
| `tradeId` | string | Original trade ID that triggered this flow |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "data": [
    {
      "symbol": "LDO-USDT",
      "incomeType": "FUNDING_FEE",
      "income": "-0.0292",
      "asset": "USDT",
      "info": "Funding Fee",
      "time": 1702713615000,
      "tranId": "170***6*2_3*9_20***97",
      "tradeId": "170***6*2_3*9_20***97"
    }
  ]
}
```

---

## 5. Export Fund Flow

`GET /openApi/swap/v2/user/income/export`

Exports fund flow records as an **Excel file** (binary response, not JSON).

> This endpoint returns a binary Excel file, not a JSON response. Handle accordingly (e.g. write to a `.xlsx` file).

**Request Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. `BTC-USDT` |
| `incomeType` | string | No | Fund flow type, optional values:REALIZED_PNL FUNDING_FEE TRADING_FEE INSURANCE_CLEAR TRIAL_FUND ADL SYSTEM_DEDUCTION |
| `startTime` | int64 | No | Start time in milliseconds |
| `endTime` | int64 | No | End time in milliseconds |
| `limit` | int | No | Number of results. Default `100`, max `1000` |

**Response:** Excel binary file (`.xlsx`). The HTTP response body is the file content directly.

**Example (download to file):**

```typescript
const res = await fetch(url, { headers: { "X-BX-APIKEY": apiKey, "X-SOURCE-KEY": "BX-AI-SKILL" } });
const buffer = await res.arrayBuffer();
fs.writeFileSync("fund_flow.xlsx", Buffer.from(buffer));
```
