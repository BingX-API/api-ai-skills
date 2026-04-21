# BingX Coin-M (CSwap) Trade — API Reference

**Base URL (Production Live):** `https://open-api.bingx.com` (fallback: `https://open-api.bingx.pro`)
**Base URL (Production Simulated):** `https://open-api-vst.bingx.com` (fallback: `https://open-api-vst.bingx.pro`)
**Authentication:** All endpoints require HMAC SHA256 signature. See [`references/authentication.md`](../references/authentication.md).
**Response format:** `{ "code": 0, "msg": "", "data": <payload> }` — `code: 0` indicates success.
**Symbol format:** `BASE-USD` (e.g., `BTC-USD`, `ETH-USD`) — coin-margined, NOT USDT-margined.

---

## 1. Place Order

### Place a New Order

`POST /openApi/cswap/v1/trade/order`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USD` |
| `side` | string | Yes | Buying and selling direction SELL, BUY |
| `positionSide` | string | No | Position direction, single position must fill in BOTH, two-way position can only choose LONG or SHORT, if it is empty, t|
| `type` | string | Yes | Order type: `MARKET`, `LIMIT`, `STOP_MARKET`, `STOP`, `TAKE_PROFIT_MARKET`, `TAKE_PROFIT` |
| `quantity` | float64 | No | Order quantity in contracts. Required unless `closePosition: true` |
| `price` | float | No | Commission price |
| `stopPrice` | float | No | Trigger price. Required for `STOP_MARKET`, `STOP`, `TAKE_PROFIT_MARKET`, `TAKE_PROFIT` |
| `timeInForce` | string | No | Effective method, currently supports GTC, IOC, FOK and PostOnly |
| `clientOrderId` | string | No | Custom order ID, 1–40 chars |
| `workingType` | string | No | Trigger price source: `MARK_PRICE` or `CONTRACT_PRICE` (default) |
| `takeProfit` | string | No | Attached take-profit (see TP/SL Object, only on `MARKET`/`LIMIT`) |
| `stopLoss` | string | No | Attached stop-loss (see TP/SL Object, only on `MARKET`/`LIMIT`) |

**TP/SL Object structure:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | `TAKE_PROFIT_MARKET`, `TAKE_PROFIT`, `STOP_MARKET`, or `STOP` |
| `stopPrice` | float | Yes | Trigger price |
| `price` | float | Conditional | Limit execution price (required for `TAKE_PROFIT` / `STOP` types) |
| `workingType` | string | No | `MARK_PRICE` or `CONTRACT_PRICE` |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `orderId` | int64 | System-generated order ID |
| `symbol` | string | Trading pair |
| `side` | string | `BUY` or `SELL` |
| `positionSide` | string | `LONG`, `SHORT`, or `BOTH` |
| `type` | string | Order type |
| `price` | float | Order price (0 for market orders) |
| `quantity` | int | Order quantity in contracts |
| `stopPrice` | float | Trigger price (0 if not applicable) |
| `workingType` | string | Trigger price source |
| `timeInForce` | string | Time in force |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "data": {
    "orderId": 1809841379603398656,
    "symbol": "BTC-USD",
    "positionSide": "LONG",
    "side": "BUY",
    "type": "LIMIT",
    "price": 65000,
    "quantity": 1,
    "stopPrice": 0,
    "workingType": "",
    "timeInForce": "GTC"
  }
}
```

---

## 2. Cancel Order

### Cancel an Order

`DELETE /openApi/cswap/v1/trade/cancelOrder`

Rate limit: 5/s per UID; 2/s per IP.

Cancel an order that is currently in a pending state.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USD` |
| `orderId` | int64 | No | Order ID |
| `clientOrderId` | string | No | Custom order ID. Required if `orderId` not provided |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `orderId` | int64 | Cancelled order ID |
| `symbol` | string | Trading pair |
| `side` | string | `BUY` or `SELL` |
| `positionSide` | string | Position direction |
| `type` | string | Order type |
| `quantity` | int | Quantity in contracts |
| `price` | float | Order price |
| `executedQty` | string | Filled quantity |
| `avgPrice` | string | Average fill price |
| `status` | string | `CANCELLED` |
| `time` | int64 | Order creation time (ms) |
| `updateTime` | int64 | Last update time (ms) |

---

## 3. Cancel All Open Orders

### Cancel All Open Orders for a Symbol

`POST /openApi/cswap/v1/trade/allOpenOrders`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. `BTC-USD` |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | array | Array of successfully cancelled order objects (same fields as Cancel Order response) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "timestamp": 1720501468364,
  "data": {
    "success": [
      {
        "symbol": "BTC-USD",
        "orderId": "1809845251327672320",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "LIMIT",
        "quantity": 1,
        "price": "65000",
        "executedQty": "0",
        "avgPrice": "0",
        "status": "CANCELLED",
        "time": 1720335707872,
        "updateTime": 1720335707912
      }
    ]
  }
}
```

---

## 4. Close All Positions

### Close All Open Positions

`POST /openApi/cswap/v1/trade/closeAllPositions`

Rate limit: 5/s per UID; 2/s per IP.

Closes all currently open positions using market orders.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. `BTC-USD`. If omitted, closes all positions across all symbols |

**Response `data`:** Empty object `{}` on success.

---

## 5. Query Open Orders

### Get All Open Orders

`GET /openApi/cswap/v1/trade/openOrders`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USD,When not filled, query all pending orders. When fill|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `orders` | array | Array of open order objects |

**Order object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `orderId` | string | System order ID |
| `side` | string | `BUY` or `SELL` |
| `positionSide` | string | `LONG`, `SHORT`, or `BOTH` |
| `type` | string | Order type |
| `quantity` | int | Quantity in contracts |
| `price` | string | Order price |
| `executedQty` | string | Filled quantity |
| `avgPrice` | string | Average fill price |
| `stopPrice` | string | Trigger price |
| `status` | string | `Pending`, `PartiallyFilled`, etc. |
| `time` | int64 | Order creation time (ms) |
| `updateTime` | int64 | Last update time (ms) |
| `clientOrderId` | string | Custom order ID |
| `takeProfit` | object | Take-profit settings |
| `stopLoss` | object | Stop-loss settings |
| `workingType` | string | Trigger price source |

---

## 6. Query Order Detail

### Get a Single Order

`GET /openApi/cswap/v1/trade/orderDetail`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USD` |
| `orderId` | int64 | No | Order ID |
| `clientOrderId` | string | No | Custom order ID. Required if `orderId` not provided |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `order` | object | Order detail object (same fields as open orders; see section 5) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "data": {
    "order": {
      "symbol": "SOL-USD",
      "orderId": "1816342420721254400",
      "side": "BUY",
      "positionSide": "Long",
      "type": "LIMIT",
      "quantity": 1,
      "price": "150",
      "executedQty": "0",
      "avgPrice": "0.000",
      "stopPrice": "",
      "profit": "0.0000",
      "commission": "0.0000",
      "status": "Pending",
      "time": 1721884753767,
      "updateTime": 1721884753786,
      "clientOrderId": "",
      "workingType": "MARK_PRICE",
      "takeProfit": {
        "type": "TAKE_PROFIT",
        "quantity": 0,
        "stopPrice": 0,
        "price": 0,
        "workingType": "MARK_PRICE",
        "stopGuaranteed": ""
      },
      "stopLoss": {
        "type": "STOP",
        "quantity": 0,
        "stopPrice": 0,
        "price": 0,
        "workingType": "MARK_PRICE",
        "stopGuaranteed": ""
      }
    }
  }
}
```

---

## 7. Query Order History

### Get Historical Orders

`GET /openApi/cswap/v1/trade/orderHistory`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USD.If no symbol is specified, it will query the histori|
| `orderId` | int64 | No | Only return subsequent orders, and return the latest order by default |
| `startTime` | int64 | No | Start time in milliseconds |
| `endTime` | int64 | No | End time in milliseconds |
| `limit` | int | Yes | Number of results (default: 100, max: 1000) |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `orders` | array | Array of historical order objects (same fields as open orders; see section 5) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "data": {
    "orders": [
      {
        "symbol": "SOL-USD",
        "orderId": "1816002957423951872",
        "side": "BUY",
        "positionSide": "LONG",
        "type": "LIMIT",
        "quantity": 1,
        "price": "150.000",
        "executedQty": "0.00000000",
        "avgPrice": "0.000",
        "status": "Filled",
        "time": 1721803819000,
        "updateTime": 1721803856000,
        "workingType": "MARK_PRICE"
      }
    ]
  }
}
```

---

## 8. Query Trade Fill History

### Get All Fill Orders (Trade History)

`GET /openApi/cswap/v1/trade/allFillOrders`

Rate limit: 5/s per UID; 2/s per IP.

> **Note:** `orderId` is required for Coin-M futures. Provide the order ID to retrieve its fill records.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `orderId` | string | Yes | Order ID |
| `pageIndex` | int64 | No | Page number |
| `pageSize` | int64 | No | Number per page, default 100, max 1000 |

**Response `data`:** Array of fill objects directly.

| Field | Type | Description |
|-------|------|-------------|
| `orderId` | string | Order ID |
| `symbol` | string | Trading pair |
| `type` | string | Order type |
| `side` | string | `BUY` or `SELL` |
| `positionSide` | string | `LONG` or `SHORT` |
| `tradeId` | string | Unique fill/trade ID |
| `volume` | string | Fill quantity in contracts |
| `tradePrice` | string | Fill price |
| `amount` | string | Fill notional value in USD |
| `realizedPnl` | string | Realized profit and loss |
| `commission` | string | Trading fee (negative = fee paid) |
| `currency` | string | Settlement asset (e.g., `BTC`) |
| `buyer` | bool | `true` if this is the buy side |
| `maker` | bool | `true` if this was a maker fill |
| `tradeTime` | int64 | Fill time (ms) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "timestamp": 1722147756019,
  "data": [
    {
      "orderId": "1817441228670648320",
      "symbol": "SOL-USD",
      "type": "MARKET",
      "side": "BUY",
      "positionSide": "LONG",
      "tradeId": "97244554",
      "volume": "2",
      "tradePrice": "182.652",
      "amount": "20.00000000",
      "realizedPnl": "0.00000000",
      "commission": "-0.00005475",
      "currency": "SOL",
      "buyer": true,
      "maker": false,
      "tradeTime": 1722146730000
    }
  ]
}
```

---

## 9. Query Liquidation Orders

### Get Liquidation / ADL Orders

`GET /openApi/cswap/v1/trade/forceOrders`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. `BTC-USD`. If omitted, returns all symbols |
| `autoCloseType` | string | No | `LIQUIDATION` (liquidation orders) or `ADL` (auto-deleveraging orders) |
| `startTime` | int64 | No | Start time in milliseconds |
| `endTime` | int64 | No | End time in milliseconds |
| `limit` | int | No | Number of results (default: 50, max: 100) |
| `recvWindow` | int64 | No | Request validity window in milliseconds |
| `timestamp` | int64 | Yes | Request timestamp in milliseconds |

**Response `data`:** Array of liquidation order objects.

| Field | Type | Description |
|-------|------|-------------|
| `orderId` | string | Order ID |
| `symbol` | string | Trading pair |
| `type` | string | Order type |
| `side` | string | `BUY` or `SELL` |
| `positionSide` | string | `LONG` or `SHORT` |
| `price` | string | Order price |
| `quantity` | float64 | Quantity in contracts |
| `stopPrice` | string | Trigger price |
| `workingType` | string | Trigger price source |
| `status` | string | Order status |
| `avgPrice` | string | Average fill price |
| `executedQty` | string | Filled quantity |
| `profit` | string | Realized profit |
| `commission` | string | Trading fee |
| `time` | int64 | Order creation time (ms) |
| `updateTime` | string | Last update time |

---

## 10. Query Leverage

### Get Current Leverage

`GET /openApi/cswap/v1/trade/leverage`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USD` |
| `recvWindow` | int64 | No | Request validity window in milliseconds |
| `timestamp` | int64 | Yes | Request timestamp in milliseconds |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `longLeverage` | int | Current long position leverage |
| `shortLeverage` | int | Current short position leverage |
| `maxLongLeverage` | int | Maximum allowed long leverage |
| `maxShortLeverage` | int | Maximum allowed short leverage |
| `availableLongVol` | string | Available long position volume (contracts) |
| `availableShortVol` | string | Available short position volume (contracts) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "timestamp": 1720683803391,
  "data": {
    "symbol": "SOL-USD",
    "longLeverage": 5,
    "shortLeverage": 5,
    "maxLongLeverage": 50,
    "maxShortLeverage": 50,
    "availableLongVol": "4000000",
    "availableShortVol": "4000000"
  }
}
```

---

## 11. Set Leverage

### Change Leverage

`POST /openApi/cswap/v1/trade/leverage`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USD` |
| `side` | string | Yes | For dual-position mode, the leverage rate of long or short positions. LONG represents long position, SHORT represents sh|
| `leverage` | string | Yes | New leverage value (e.g., `10`, `20`) |
| `recvWindow` | int64 | No | Request validity window in milliseconds |
| `timestamp` | int64 | Yes | Request timestamp in milliseconds |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `longLeverage` | int | Updated long leverage |
| `shortLeverage` | int | Updated short leverage |

---

## 12. Query Margin Type

### Get Current Margin Mode

`GET /openApi/cswap/v1/trade/marginType`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USD` |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `marginType` | string | `CROSSED` (cross margin) or `ISOLATED` (isolated margin) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "timestamp": 1721966069132,
  "data": {
    "symbol": "SOL-USD",
    "marginType": "CROSSED"
  }
}
```

---

## 13. Set Margin Type

### Change Margin Mode

`POST /openApi/cswap/v1/trade/marginType`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USD` |
| `marginType` | string | Yes | Margin type, e.g., ISOLATED, CROSSED |
| `recvWindow` | int64 | No | Request validity window in milliseconds |
| `timestamp` | int64 | Yes | Request timestamp in milliseconds |

**Response `data`:** Empty object `{}` on success.

---

## 14. Adjust Position Margin

### Add or Remove Isolated Margin

`POST /openApi/cswap/v1/trade/positionMargin`

Rate limit: 5/s per UID; 2/s per IP.

Adjusts the margin amount for an isolated position. Only applicable when margin type is `ISOLATED`.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USD` |
| `positionSide` | string | Yes | `LONG` or `SHORT` |
| `amount` | float | Yes | Margin funds |
| `type` | int | Yes | Margin adjustment type: `1` = add, `2` = reduce |

**Response `data`:** Empty object `{}` on success.

---

## 15. Query Commission Rate

### Get Trading Commission Rate

`GET /openApi/cswap/v1/user/commissionRate`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

No endpoint-specific parameters.

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `takerCommissionRate` | string | Taker fee rate (e.g., `"0.0005"` = 0.05%) |
| `makerCommissionRate` | string | Maker fee rate (e.g., `"0.0002"` = 0.02%) |

**Example response:**

```json
{
  "code": 0,
  "msg": "",
  "timestamp": 1721365261438,
  "data": {
    "takerCommissionRate": "0.0005",
    "makerCommissionRate": "0.0002"
  }
}
```

---

## 16. Query Account Assets

`GET /openApi/cswap/v1/user/balance`

Rate limit: 5/s per UID; 2/s per IP.

Query coin-margined account asset balances.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. BTC-USD; omit for all assets |

**Response `data` (array):**

| Field | Type | Description |
|-------|------|-------------|
| `asset` | string | Asset name |
| `balance` | string | Total balance |
| `equity` | string | Asset net value |
| `unrealizedProfit` | string | Unrealized profit and loss |
| `availableMargin` | string | Available margin |
| `usedMargin` | string | Used margin |
| `freezedMargin` | string | Frozen margin |
| `shortUid` | string | User UID |

---

## 17. Get Current Positions

`GET /openApi/cswap/v1/user/positions`

Rate limit: 5/s per UID; 2/s per IP.

Query current open positions for coin-margined contracts.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. BTC-USD; omit for all positions |

**Response `data` (array):**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `positionId` | string | Position ID |
| `positionSide` | string | Position direction: `LONG` or `SHORT` |
| `isolated` | bool | `true` = isolated margin; `false` = cross margin |
| `positionAmt` | string | Position quantity |
| `availableAmt` | string | Closeable quantity |
| `unrealizedProfit` | string | Unrealized profit and loss |
| `initialMargin` | string | Initial margin |
| `liquidationPrice` | float64 | Liquidation price |
| `avgPrice` | string | Average entry price |
| `leverage` | int32 | Leverage |
| `markPrice` | string | Mark price |
| `riskRate` | string | Risk rate |
| `maxMarginReduction` | string | Maximum margin reduction |
| `updateTime` | int64 | Last update time (ms) |

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
| `109425` | The trading pair does not exist or is not supported. Call /openApi/cswap/v1/quote/contracts to verify. |
| `109500` | Internal server error. If it persists, retry later or contact support. |
| `110206` | TP/SL orders reached the maximum limit. Cancel some existing TP/SL orders first. |
| `110400` | The submitted order parameters do not meet the requirements. Verify price, quantity, etc. |
| `110500` | Order system busy. Please retry later. |

For the complete error code list, see [Error Code Reference](../references/error-codes.md).
