# BingX Perpetual Swap Trade — API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

**Common parameters** (apply to all endpoints below):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | int64 | Yes | Request timestamp in milliseconds |
| recvWindow | int64 | No | Request validity window in ms, max 5000 |

---

## I. Place Orders

### 1. Place Order

`POST /openApi/swap/v2/trade/order`

Rate limit: 10/s per UID; 3/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `side` | string | Yes | buying and selling direction SELL, BUY |
| `positionSide` | string | No | Position direction, required for single position as BOTH, for both long and short positions only LONG or SHORT can be ch|
| `type` | string | Yes | Order type: `MARKET`, `LIMIT`, `STOP_MARKET`, `STOP`, `TAKE_PROFIT_MARKET`, `TAKE_PROFIT`, `TRAILING_STOP_MARKET`, `TRAILING_TP_SL` |
| `quantity` | float | No | Original quantity, only support units by COIN ,Ordering with quantity U is not currently supported. |
| `quoteOrderQty` | float | No | Quote order quantity, e.g., 100USDT,if quantity and quoteOrderQty are input at the same time, quantity will be used firs|
| `price` | float | No | Price, represents the trailing stop distance in TRAILING_STOP_MARKET and TRAILING_TP_SL |
| `stopPrice` | float | No | Trigger price (required for `STOP_MARKET`, `STOP`, `TAKE_PROFIT_MARKET`, `TAKE_PROFIT`) |
| `timeInForce` | string | No | Time in force: `GTC`, `IOC`, `FOK`, `PostOnly`; required for `LIMIT`, default `GTC` |
| `clientOrderId` | string | No | Custom order ID, 1–40 characters, converted to lowercase by the system; must be unique per order; **supported for `MARKET` and `LIMIT` only** |
| `workingType` | string | No | Trigger price source: `MARK_PRICE` (mark price, **default**), `CONTRACT_PRICE` (last trade price), or `INDEX_PRICE` (index price); must be `CONTRACT_PRICE` when `stopGuaranteed=true` or `cutfee` |
| `stopGuaranteed` | string | No | true: Enables the guaranteed stop-loss and take-profit feature; false: Disables the feature; cutfee: Enable the guaranteed stop loss function and enable the VIP guaranteed stop loss fee reduction function. When stopGuaranteed is true or cutfee, the quantity field does not take effect. The guaranteed stop-loss feature is not enabled by default. Supported order types include: STOP_MARKET / TAKE_PROFIT_MARKET / STOP / TAKE_PROFIT / TRIGGER_LIMIT / TRIGGER_MARKET. |
| `closePosition` | string | No | `true` closes all positions in the specified direction on trigger; cannot be used with `quantity` |
| `reduceOnly` | string | No | true, false; Default value is false for single position mode; This parameter is not accepted for both long and short pos|
| `activationPrice` | float | No | Activation price (for `TRAILING_STOP_MARKET`; defaults to current market price if omitted) |
| `priceRate` | float | No | Callback rate (required for `TRAILING_STOP_MARKET` and `TRAILING_TP_SL`, e.g. `0.05` = 5%) |
| `stopLoss` | string | No | Stop-loss attached order (may only be attached to `MARKET` / `LIMIT` orders; see structure below) |
| `takeProfit` | string | No | Support setting take profit while placing an order. Only supports type: TAKE_PROFIT_MARKET/TAKE_PROFIT |
| `positionId` | int | No | In the Separate Isolated mode, closing a position must be transmitted |

**stopLoss / takeProfit object structure:**

```json
{
  "type": "STOP_MARKET",       // stopLoss: "STOP_MARKET" or "STOP"
                               // takeProfit: "TAKE_PROFIT_MARKET" or "TAKE_PROFIT"
  "stopPrice": 29000,          // Trigger price (required)
  "price": 28900,              // Limit execution price (required when type is "STOP" or "TAKE_PROFIT")
  "workingType": "MARK_PRICE", // Trigger price source: "MARK_PRICE" or "CONTRACT_PRICE"
  "stopGuaranteed": false      // Whether to guarantee fill
}
```

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `orderId` | int | System order ID (numeric — may lose precision in JavaScript for large values) |
| `orderID` | string | System order ID (string — use this in JavaScript/TypeScript to avoid precision loss) |
| `symbol` | string | Trading pair |
| `side` | string | Order side |
| `positionSide` | string | Position side |
| `type` | string | Order type |
| `origQty` | string | Order quantity |
| `price` | string | Order price |
| `stopPrice` | string | Trigger price |
| `workingType` | string | Trigger price source |
| `status` | string | Order status: `NEW`, `PARTIALLY_FILLED`, `FILLED`, `CANCELED`, `EXPIRED` |
| `clientOrderId` | string | Custom order ID |

> **Important:** BingX order IDs can exceed JavaScript's `Number.MAX_SAFE_INTEGER`. Always use the string `orderID` field (capital "ID") instead of the numeric `orderId` field when working in JavaScript/TypeScript to avoid precision loss.

---

### 2. Test Place Order

`POST /openApi/swap/v2/trade/order/test`

Rate limit: 5/s per UID; 2/s per IP.

Parameters are identical to the Place Order endpoint. No actual trade is executed; used to validate signature and parameter correctness. Response structure is the same as Place Order.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `side` | string | Yes | buying and selling direction SELL, BUY |
| `type` | string | Yes | Order type: `MARKET`, `LIMIT`, `STOP_MARKET`, `STOP`, `TAKE_PROFIT_MARKET`, `TAKE_PROFIT`, `TRAILING_STOP_MARKET`, `TRAILING_TP_SL` |
| `positionSide` | string | No | Position direction, required for single position as BOTH, for both long and short positions only LONG or SHORT can be ch|
| `reduceOnly` | string | No | true, false; Default value is false for single position mode; This parameter is not accepted for both long and short pos|
| `price` | float64 | No | Price, represents the trailing stop distance in TRAILING_STOP_MARKET and TRAILING_TP_SL |
| `quantity` | float64 | No | Original quantity, only support units by COIN ,Ordering with quantity U is not currently supported. |
| `stopPrice` | float64 | No | Trigger price (required for stop/take-profit types) |
| `priceRate` | float64 | No | For type: TRAILING_STOP_MARKET or TRAILING_TP_SL; Maximum: 1 |
| `stopLoss` | string | No | Support setting stop loss while placing an order. Only supports type: STOP_MARKET/STOP |
| `takeProfit` | string | No | Support setting take profit while placing an order. Only supports type: TAKE_PROFIT_MARKET/TAKE_PROFIT |
| `clientOrderId` | string | No | Customized order ID for users, with a limit of characters from 1 to 40. Different orders cannot use the same clientOrder|
| `timeInForce` | string | No | Time in force: `GTC`, `IOC`, `FOK`, `PostOnly` |
| `closePosition` | string | No | true, false; all position squaring after triggering, only support STOP_MARKET and TAKE_PROFIT_MARKET; not used with quan|
| `activationPrice` | float64 | No | Used with TRAILING_STOP_MARKET or TRAILING_TP_SL orders, default as the latest price(supporting different workingType) |
| `stopGuaranteed` | string | No | true: Enables the guaranteed stop-loss and take-profit feature; false: Disables the feature; cutfee: Enable the guaranteed stop loss function and enable the VIP guaranteed stop loss fee reduction function. When stopGuaranteed is true or cutfee, the quantity field does not take effect. The guaranteed stop-loss feature is not enabled by default. Supported order types include: STOP_MARKET: Market stop-loss order / TAKE_PROFIT_MARKET: Market take-profit order / STOP: Limit stop-loss order / TAKE_PROFIT: Limit take-profit order / TRIGGER_LIMIT: Stop-limit order with trigger / TRIGGER_MARKET: Market order with trigger for stop-loss. |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair, e.g. `BTC-USDT` |
| `orderId` | int64 | Order ID |
| `side` | string | Order direction: `BUY` / `SELL` |
| `positionSide` | string | `BOTH`, `LONG`, or `SHORT` |
| `type` | string | Order type |
| `clientOrderId` | string | Custom order ID (if provided) |
| `workingType` | string | Trigger price type, e.g. `MARK_PRICE` |

---

### 3. Batch Place Orders

`POST /openApi/swap/v2/trade/batchOrders`

Rate limit: 5/s per UID; 3/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `batchOrders` | LIST<Order> | Yes | Array of orders, up to 5; each order uses the same structure as Place Order |

> Note: `batchOrders` is a JSON array. URL-encode the parameter value when it contains `[` or `{`.

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `orders` | array | List of successfully placed orders |
| `errors` | array | List of failed orders with error details |

---

## II. Cancel Orders

### 4. Cancel Single Order

`DELETE /openApi/swap/v2/trade/order`

Rate limit: 10/s per UID; 3/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `orderId` | int | No | Order ID |
| `clientOrderId` | string | No | Customized order ID for users, with a limit of characters from 1 to 40. The system will convert this field to lowercase.|

**Response `data`:** Details of the cancelled order (same fields as Place Order response).

---

### 5. Batch Cancel Orders

`DELETE /openApi/swap/v2/trade/batchOrders`

Rate limit: 5/s per UID; 3/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT |
| `orderIdList` | LIST<int64> | No | system order number, up to 10 orders [1234567,2345678] |
| `clientOrderIdList` | LIST<string> | No | Customized order ID for users, up to 10 orders ["abc1234567","abc2345678"]. The system will convert this field to lowerc|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | array | List of successfully cancelled orders |
| `failed` | array | List of failed cancellations with error details |

---

### 6. Cancel All Open Orders

`DELETE /openApi/swap/v2/trade/allOpenOrders`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT,if you do not fill this field,will delete all type |
| `type` | string | No | LIMIT: Limit Order / MARKET: Market Order / STOP_MARKET: Stop Market Order / TAKE_PROFIT_MARKET: Take Profit Market Orde|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | array | List of successfully cancelled orders |
| `failed` | array | List of failed cancellations with error details |

---

### 7. Cancel All After (Kill Switch)

`POST /openApi/swap/v2/trade/cancelAllAfter`

Rate limit: 1/s per UID; 2/s per IP.

Starts or stops a countdown timer. When the timer expires, all open orders are automatically cancelled. Useful to prevent orders from lingering after a network disconnection.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Request type: ACTIVATE-Activate, CLOSE-Close |
| `timeOut` | int | Yes | Countdown duration (seconds), range 10–120 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `triggerTime` | int | Timestamp (ms) when auto-cancel will trigger; returns `0` when `CLOSE` |
| `status` | string | Operation result: `ACTIVATED`, `CLOSED`, or `FAILED` |
| `note` | string | Additional information |

---

## III. Order Queries

### 8. Query Single Open Order Status

`GET /openApi/swap/v2/trade/openOrder`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT |
| `orderId` | int | No | Order ID |
| `clientOrderId` | string | No | Customized order ID for users, with a limit of characters from 1 to 40. Different orders cannot use the same clientOrder|

**Response `data`:** Open order object with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `orderId` | int | Order ID |
| `symbol` | string | Trading pair |
| `side` | string | Order side |
| `positionSide` | string | Position side |
| `type` | string | Order type |
| `origQty` | string | Order quantity |
| `executedQty` | string | Filled quantity |
| `price` | string | Order price |
| `avgPrice` | string | Average fill price |
| `status` | string | Order status: `NEW`, `PARTIALLY_FILLED`, `FILLED`, `CANCELED`, `EXPIRED` |
| `time` | int | Order placement time (milliseconds) |
| `updateTime` | int | Last update time (milliseconds) |

---

### 9. Query Order Details

`GET /openApi/swap/v2/trade/order`

Rate limit: 30/s per UID; 2/s per IP.

Query an order by orderId or clientOrderId. Can retrieve orders in any status (including filled or cancelled).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `orderId` | int64 | No | Order ID |
| `clientOrderId` | string | No | Customized order ID for users, with a limit of characters from 1 to 40. The system will convert this field to lowercase.|

**Response `data`:** Order object with the same fields as "Query Single Open Order Status".

---

### 10. Query All Current Open Orders

`GET /openApi/swap/v2/trade/openOrders`

Rate limit: 5/s per UID; 3/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT,When not filled, query all pending orders. When fil|
| `type` | string | No | LIMIT: Limit Order / MARKET: Market Order / STOP_MARKET: Stop Market Order / TAKE_PROFIT_MARKET: Take Profit Market Orde|

**Response `data`:** Array of open order objects; each object has the same fields as "Query Single Open Order Status".

---

### 11. Order History

`GET /openApi/swap/v2/trade/allOrders`

Rate limit: 5/s per UID; 3/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT.If no symbol is specified, it will query the histor|
| `currency` | string | No | Settlement currency: `USDT` or `USDC` |
| `orderId` | int | No | Only return subsequent orders, and return the latest order by default |
| `startTime` | int | No | Start time (millisecond timestamp) |
| `endTime` | int | No | End time (millisecond timestamp) |
| `limit` | int | Yes | Number of results, default 500, max 1000 |

> **Note:** When using `startTime` and `endTime`, the query range must not exceed **7 days**. The server returns error `109400` if the range is larger.

**Response `data`:** Array of historical orders; each object has the same fields as "Query Single Open Order Status".

---

### 12. Liquidation / Force Close Order Query

`GET /openApi/swap/v2/trade/forceOrders`

Rate limit: 10/s per UID; 2/s per IP.

Query forced liquidation orders triggered by liquidation (LIQUIDATION) or auto-deleveraging (ADL).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT |
| `currency` | string | No | Settlement currency: `USDT` or `USDC` |
| `autoCloseType` | string | No | `LIQUIDATION` or `ADL` |
| `startTime` | int | No | Start time (millisecond timestamp) |
| `endTime` | int | No | End time (millisecond timestamp) |
| `limit` | int | No | The number of returned result sets The default value is 50, the maximum value is 100 |

**Response `data`:** Array of forced liquidation orders; same fields as "Order History".

---

### 13. Trade Fill History

`GET /openApi/swap/v2/trade/allFillOrders`

Rate limit: 5/s per UID; 2/s per IP.

Query individual trade fills for the account, returning detailed information for each actual execution (including fees and realized PnL).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tradingUnit` | string | Yes | Trading unit, optional values: COIN,CONT; COIN directly represent assets such as BTC and ETH, and CONT represents the nu|
| `startTs` | int | Yes | Start time (millisecond timestamp) |
| `endTs` | int | Yes | End time (millisecond timestamp) |
| `orderId` | int | No | If orderId is provided, only the filled orders of that orderId are returned |
| `currency` | string | No | Settlement currency: `USDT` or `USDC` |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `tradeId` | int | Trade fill ID |
| `symbol` | string | Trading pair |
| `orderId` | int | Order ID |
| `side` | string | Fill side |
| `price` | string | Fill price |
| `qty` | string | Fill quantity |
| `realizedPnl` | string | Realized PnL |
| `fee` | string | Fee (negative value = paid out) |
| `time` | int | Fill time (milliseconds) |

---

## IV. Position Management

### 14. Close All Positions

`POST /openApi/swap/v2/trade/closeAllPositions`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, for example: BTC-USDT, please use capital letters. |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | array | List of successfully closed position IDs |
| `failed` | array | List of positions that failed to close with error details |

---

### 15. Close Position by positionId

`POST /openApi/swap/v1/trade/closePosition`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `positionId` | string | Yes | Position ID, will close the position with market price |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `orderId` | int | Order ID generated by the position close |
| `positionId` | string | ID of the closed position |

---

### 16. Adjust Isolated Margin

`POST /openApi/swap/v2/trade/positionMargin`

Rate limit: 2/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT |
| `amount` | float | Yes | Margin adjustment amount (USDT) |
| `positionSide` | string | No | Position side: `LONG` or `SHORT` |
| `positionId` | int | No | Position ID, if it is filled, the system will use the positionId first |
| `type` | int | Yes | adjustment direction 1: increase isolated margin, 2: decrease isolated margin |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `amount` | float | Adjustment amount |
| `type` | int | Adjustment direction |

---

## V. Leverage and Mode Settings

### 17. Query Margin Mode

`GET /openApi/swap/v2/trade/marginType`

Rate limit: 2/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `marginType` | string | Current margin mode: `ISOLATED` or `CROSSED` |

---

### 18. Switch Margin Mode

`POST /openApi/swap/v2/trade/marginType`

Rate limit: 2/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT |
| `marginType` | string | Yes | Target margin mode: `ISOLATED`, `CROSSED`, or `SEPARATE_ISOLATED` (isolated-split mode — allows multiple independent isolated positions for the same pair; `positionId` required when closing) |

**Response `data`:** Empty object (success returns `code: 0`).

---

### 19. Query Leverage and Available Position

`GET /openApi/swap/v2/trade/leverage`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `longLeverage` | int | Current long leverage |
| `shortLeverage` | int | Current short leverage |
| `maxLongLeverage` | int | Maximum long leverage |
| `maxShortLeverage` | int | Maximum short leverage |
| `availableLongVol` | string | Available quantity to open long |
| `availableShortVol` | string | Available quantity to open short |

---

### 20. Set Leverage

`POST /openApi/swap/v2/trade/leverage`

Rate limit: 5/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | There must be a hyphen/ "-" in the trading pair symbol. eg: BTC-USDT |
| `side` | string | Yes | Side to set: `LONG`, `SHORT` (hedge mode) or `BOTH` (one-way mode) |
| `leverage` | int | Yes | Leverage multiplier |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair |
| `leverage` | int | Leverage after update |
| `availableVol` | string | Available quantity to open at current leverage |
| `maxVol` | string | Maximum openable quantity |

---

### 21. Query Position Mode

`GET /openApi/swap/v1/positionSide/dual`

Rate limit: 2/s per UID; 2/s per IP.

**Parameters:** No additional parameters beyond [common parameters](#common-parameters).

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `dualSidePosition` | bool | `true` = hedge (dual-side) mode; `false` = one-way mode |

---

### 22. Set Position Mode

`POST /openApi/swap/v1/positionSide/dual`

Rate limit: 4/s per UID; 2/s per IP.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dualSidePosition` | true | Yes | `"true"` switches to hedge mode; `"false"` switches to one-way mode |

> Note: Ensure there are no open orders or positions before switching position mode, otherwise an error will be returned.

**Response `data`:** Empty object (success returns `code: 0`).

---

## VI. Order Modification and Replacement

### 23. Amend Order

`POST /openApi/swap/v1/trade/amend`

Rate limit: 5/s per UID.

Modifies the quantity of an existing open order. The order must still be open (`NEW` or `PARTIALLY_FILLED`).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `orderId` | string | Yes | System order ID (at least one of `orderId` or `clientOrderId` required) |
| `clientOrderId` | string | Yes | Custom order ID (at least one of `orderId` or `clientOrderId` required) |
| `quantity` | float | Yes | New order quantity after amendment |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `orderId` | string | Order ID |
| `clientOrderId` | string | Custom order ID |
| `symbol` | string | Trading pair |
| `quantity` | string | Updated order quantity |

---

### 24. Cancel and Replace Order

`POST /openApi/swap/v1/trade/cancelReplace`

Rate limit: 5/s per UID; 2/s per IP.

Atomic operation: cancels an existing open order and immediately submits a new order, eliminating the time-window risk between cancel and re-submit.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. `BTC-USDT` |
| `cancelOrderId` | int | No | System order ID to cancel (at least one of `cancelOrderId` or `cancelClientOrderId` required) |
| `cancelClientOrderId` | string | No | The original client-defined order ID to be canceled. The system will convert this field to lowercase. Either cancelClien|
| `side` | string | Yes | buying and selling direction SELL, BUY |
| `positionSide` | string | Yes | Position direction, required for single position as BOTH, for both long and short positions only LONG or SHORT can be ch|
| `type` | string | Yes | LIMIT: Limit Order / MARKET: Market Order / STOP_MARKET: Stop Market Order / TAKE_PROFIT_MARKET: Take Profit Market Orde|
| `quantity` | float | No | Original quantity, only support units by COIN ,Ordering with quantity U is not currently supported. |
| `price` | float | No | Price, represents the trailing stop distance in TRAILING_STOP_MARKET and TRAILING_TP_SL |
| `cancelReplaceMode` | string | Yes | STOP_ON_FAILURE: If the order cancellation fails, the replacement order will not continue. ALLOW_FAILURE: Regardless of whether the cancellation succeeds or not, a new order is placed. |
| `cancelRestrictions` | string | No | ONLY_NEW: If the order status is NEW, the cancellation will succeed. ONLY_PENDING: If the order status is PENDING, the cancellation will succeed. ONLY_PARTIALLY_FILLED: If the order status is PARTIALLY_FILLED, the cancellation will succeed. |
| `reduceOnly` | string | No | true, false; Default value is false for single position mode; This parameter is not accepted for both long and short position mode. |
| `stopPrice` | float64 | No | Trigger price (for stop/take-profit types) |
| `priceRate` | float64 | No | For type: TRAILING_STOP_MARKET or TRAILING_TP_SL ; Maximum: 1 |
| `workingType` | string | No | StopPrice trigger price types: MARK_PRICE, CONTRACT_PRICE,  default MARK_PRICE. When the type is STOP or STOP_MARKET, an|
| `stopLoss` | string | No | Support setting stop loss while placing an order. Only supports type: STOP_MARKET/STOP |
| `takeProfit` | string | No | Support setting take profit while placing an order. Only supports type: TAKE_PROFIT_MARKET/TAKE_PROFIT |
| `clientOrderId` | string | No | Customized order ID for users, with a limit of characters from 1 to 40. The system will convert this field to lowercase.|
| `closePosition` | string | No | true, false; all position squaring after triggering, only support STOP_MARKET and TAKE_PROFIT_MARKET; not used with quan|
| `activationPrice` | float64 | No | Used with TRAILING_STOP_MARKET or TRAILING_TP_SL  orders, default as the latest price(supporting different workingType) |
| `stopGuaranteed` | string | No | true: Enables the guaranteed stop-loss and take-profit feature; false: Disables the feature. The guaranteed stop-loss fe|
| `timeInForce` | string | No | Time in force: `GTC`, `IOC`, `FOK`, `PostOnly` |
| `positionId` | int64 | No | In the Separate Isolated mode, closing a position must be transmitted |

> Other new order parameters follow the same rules as Place Order (§1).

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `cancelResult` | string | Cancel result: `SUCCESS` or `FAILED` |
| `newOrderResult` | string | New order result: `SUCCESS` or `FAILED` |
| `cancelOrderId` | int | ID of the cancelled order |
| `newOrderId` | int | ID of the new order |

---

### 25. Batch Cancel and Replace Orders (batchCancelReplace)

`POST /openApi/swap/v1/trade/batchCancelReplace`

Rate limit: 2/s per UID; 2/s per IP.

Batch atomic operation: simultaneously cancels multiple open orders and submits multiple new orders. Each operation executes independently; partial failures do not affect other orders.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `batchOrders` | string | Yes | A batch of orders, string form of LIST<OrderRequest> |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `result` | array | List of results for each operation; same fields as Cancel and Replace response |

---

## VII. TWAP Orders

### 26. Place TWAP Order

`POST /openApi/swap/v1/twap/order`

Rate limit: 2/s per UID; 2/s per IP.

Place a Time-Weighted Average Price (TWAP) order that splits a large order into smaller child orders executed at regular intervals.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. BTC-USDT |
| `side` | string | Yes | Buying and selling direction SELL, BUY |
| `positionSide` | string | Yes | `LONG` or `SHORT` |
| `priceType` | string | Yes | `constant` (price interval) or `percentage` (slippage) |
| `priceVariance` | string | Yes | Price difference in USDT (constant) or slippage percentage (percentage) |
| `triggerPrice` | string | Yes | Trigger price, this price is the condition that limits the execution of strategy orders. For buying, when the market pri|
| `interval` | int64 | Yes | After the strategic order is split, the time interval for order placing is between 5-120s. |
| `amountPerOrder` | string | Yes | The quantity of a single order. After the strategy order is split, the maximum order quantity for a single order。 |
| `totalAmount` | string | Yes | The total number of orders. The total trading volume of strategy orders, which may be split into multiple order executio|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `mainOrderId` | string | TWAP main order ID |

---

### 27. Cancel TWAP Order

`POST /openApi/swap/v1/twap/cancelOrder`

Rate limit: 2/s per UID; 2/s per IP.

Cancel an active TWAP order.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mainOrderId` | string | Yes | TWAP order ID to cancel |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `mainOrderId` | string | Cancelled TWAP order ID |

---

### 28. Query TWAP Open Orders

`GET /openApi/swap/v1/twap/openOrders`

Rate limit: 2/s per UID; 2/s per IP.

Query currently active TWAP orders.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. BTC-USDT; omit for all |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `mainOrderId` | string | TWAP main order ID |
| `symbol` | string | Trading pair |
| `side` | string | `BUY` or `SELL` |
| `positionSide` | string | `LONG` or `SHORT` |
| `priceType` | string | `constant` or `percentage` |
| `priceVariance` | string | Price variance value |
| `triggerPrice` | string | Trigger price |
| `interval` | int64 | Interval in seconds |
| `amountPerOrder` | string | Quantity per child order |
| `totalAmount` | string | Total volume |
| `executedQty` | string | Executed quantity |
| `status` | string | Order status |

---

### 29. Query TWAP Historical Orders

`GET /openApi/swap/v1/twap/historyOrders`

Rate limit: 2/s per UID; 2/s per IP.

Query historical (completed/cancelled) TWAP orders.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. BTC-USDT; omit for all |
| `pageIndex` | int64 | Yes | Page number, min 1 |
| `pageSize` | int64 | Yes | Page size, max 1000 |
| `startTime` | int64 | Yes | Start time in milliseconds |
| `endTime` | int64 | Yes | End time in milliseconds |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total number of records |
| `list` | array | Array of TWAP order objects (same fields as open orders plus completion info) |

---

### 30. TWAP Order Details

`GET /openApi/swap/v1/twap/orderDetail`

Rate limit: 2/s per UID; 2/s per IP.

Query detailed information about a specific TWAP order, including child order execution records.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mainOrderId` | string | Yes | TWAP order ID |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `mainOrderId` | string | TWAP main order ID |
| `symbol` | string | Trading pair |
| `side` | string | `BUY` or `SELL` |
| `positionSide` | string | `LONG` or `SHORT` |
| `totalAmount` | string | Total volume |
| `executedQty` | string | Executed quantity |
| `status` | string | Order status |
| `childOrders` | array | Array of child order execution records |

---

## VIII. Multi-Assets Mode

### 31. Query Multi-Assets Mode

`GET /openApi/swap/v1/trade/assetMode`

Rate limit: 2/s per UID; 2/s per IP.

Query the current multi-assets mode setting.

**Parameters:** No additional parameters beyond [common parameters](#common-parameters).

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `assetMode` | string | `singleAssetMode` or `multiAssetsMode` |

---

### 32. Switch Multi-Assets Mode

`POST /openApi/swap/v1/trade/assetMode`

Rate limit: 2/s per UID; 2/s per IP.

Switch between single-asset mode and multi-assets mode. Cannot switch when there are open positions or orders.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `assetMode` | string | Yes | `singleAssetMode` or `multiAssetsMode` |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `assetMode` | string | Updated asset mode |

---

### 33. Query Multi-Assets Rules

`GET /openApi/swap/v1/trade/multiAssetsRules`

Rate limit: 2/s per IP.

Query multi-assets mode rules including supported margin assets and their discount rates.

**Parameters:** No additional parameters beyond [common parameters](#common-parameters).

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `rules` | array | List of margin asset rules |

---

### 34. Query Multi-Assets Margin

`GET /openApi/swap/v1/user/marginAssets`

Rate limit: 2/s per UID; 2/s per IP.

Query margin assets and their valuations under multi-assets mode.

**Parameters:** No additional parameters beyond [common parameters](#common-parameters).

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `assets` | array | List of margin asset details |

---

## IX. Additional Endpoints

### 35. All Orders (V2)

`GET /openApi/swap/v1/trade/fullOrder`

Rate limit: 5/s per UID; 2/s per IP.

Query all orders (open, filled, cancelled) with extended filter options. Supports pagination.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | No | Trading pair, e.g. BTC-USDT; omit for all pairs |
| `orderId` | int64 | No | Only return orders after this ID |
| `startTime` | int64 | No | Start time in milliseconds |
| `endTime` | int64 | No | End time in milliseconds |
| `limit` | int | Yes | Number of results, default 500, max 1000 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `orders` | array | Array of order objects (same fields as Query All Orders) |

---

### 36. Query Historical Transaction Details

`GET /openApi/swap/v2/trade/fillHistory`

Rate limit: 5/s per UID; 2/s per IP.

Query historical fill/transaction details with pagination support.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. BTC-USDT |
| `currency` | string | No | `USDC` or `USDT` |
| `orderId` | int64 | No | If orderId is provided, only the filled orders of that orderId are returned |
| `lastFillId` | int64 | No | Last tradeId from previous query, default 0 |
| `startTs` | int64 | Yes | Start timestamp in milliseconds |
| `endTs` | int64 | Yes | End timestamp in milliseconds |
| `pageIndex` | int64 | No | Page number, default 1 |
| `pageSize` | int64 | No | The size of each page must be greater than 0, the maximum value is 1000, if you do not fill in, then the default 50 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `fill_orders` | array | Array of fill detail objects |

---

### 37. Query Position History

`GET /openApi/swap/v1/trade/positionHistory`

Rate limit: 5/s per UID; 2/s per IP.

Query closed position history with pagination.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. BTC-USDT |
| `currency` | string | No | `USDC` or `USDT` |
| `positionId` | int64 | No | Position ID; omit for all position histories of the pair |
| `startTs` | int64 | Yes | Start timestamp in milliseconds, max span 3 months |
| `endTs` | int64 | Yes | End timestamp in milliseconds, max span 3 months |
| `pageIndex` | int64 | No | Page number, default 1 |
| `pageSize` | int64 | No | Page size, must be greater than 0, maximum value is 100, if not provided, the default is 1000 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total records |
| `list` | array | Array of historical position objects |

---

### 38. Isolated Margin Change History

`GET /openApi/swap/v1/positionMargin/history`

Rate limit: 5/s per UID; 2/s per IP.

Query the margin adjustment history for isolated-margin positions.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. BTC-USDT |
| `positionId` | string | Yes | Position ID |
| `startTime` | int64 | Yes | Start timestamp in milliseconds |
| `endTime` | int64 | Yes | End timestamp in milliseconds |
| `pageIndex` | int64 | Yes | Page number, default 1 |
| `pageSize` | int64 | Yes | Page size, max 100 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total records |
| `list` | array | Array of margin change records |

---

### 39. Position and Maintenance Margin Ratio

`GET /openApi/swap/v1/maintMarginRatio`

Rate limit: 5/s per UID; 2/s per IP.

Query the maintenance margin ratio tiers for a trading pair.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. BTC-USDT |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `tiers` | array | Array of margin ratio tier objects |

---

### 40. Automatic Margin Addition

`POST /openApi/swap/v1/trade/autoAddMargin`

Rate limit: 2/s per UID; 2/s per IP.

Enable or disable automatic margin addition for a position in hedge mode.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading pair, e.g. BTC-USDT |
| `positionId` | int64 | Yes | Position ID |
| `functionSwitch` | string | Yes | `true` to enable, `false` to disable |
| `amount` | string | No | Margin amount in USDT (when enabling) |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the operation succeeded |

---

### 41. One-Click Reverse Position

`POST /openApi/swap/v1/trade/reverse`

Rate limit: 2/s per UID; 2/s per IP.

Reverse a position direction with one click. Supports immediate or trigger-based reversal.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | `Reverse` (immediate) or `TriggerReverse` (planned) |
| `symbol` | string | Yes | Trading pair, e.g. BTC-USDT |
| `triggerPrice` | string | No | Trigger price (required for `TriggerReverse`) |
| `workingType` | string | No | `MARK_PRICE` or `CONTRACT_PRICE` (required for `TriggerReverse`) |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `orderId` | int | Reverse order ID |

---

### 42. Apply VST

`POST /openApi/swap/v2/trade/getVst`

Rate limit: 5/s per UID; 2/s per IP.

Apply for or adjust Virtual Simulated Trading (VST) balance.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `adjustType` | string | No | `0` to increase, `1` to decrease |
| `amount` | int64 | No | Adjustment amount |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `balance` | string | Updated VST balance |

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
| `109425` | The trading pair does not exist or is not supported. Call /openApi/swap/v2/quote/contracts to verify. |

Rate limit: 1/s per IP.

| `109500` | Internal server error. If it persists, retry later or contact support. |
| `110206` | TP/SL orders reached the maximum limit. Cancel some existing TP/SL orders first. |
| `110400` | The submitted order parameters do not meet the requirements. Verify price, quantity, etc. |
| `110500` | Order system busy. Please retry later. |

For the complete error code list, see [Error Code Reference](../references/error-codes.md).
