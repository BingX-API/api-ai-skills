# BingX Spot Trade — API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

**Common parameters** (apply to all endpoints below):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timestamp | int64 | Yes | Request timestamp in milliseconds |
| recvWindow | int64 | No | Request validity window in ms, max 5000 |

---

## Place Order

### POST /openApi/spot/v1/trade/order — Place Order

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, format `BASE-QUOTE`, e.g. `BTC-USDT` |
| side | string | Yes | Side: `BUY` / `SELL` |
| type | string | Yes | Order type: `MARKET` / `LIMIT` / `TAKE_STOP_LIMIT` / `TAKE_STOP_MARKET` / `TRIGGER_LIMIT` / `TRIGGER_MARKET` |
| quantity | float64 | No | Original quantity, e.g., 0.1BTC |
| quoteOrderQty | float64 | No | Quote order quantity, e.g., 100USDT,if quantity and quoteOrderQty are input at the same time, quantity will be used firs|
| price | float64 | No | Price, e.g., 10000USDT |
| stopPrice | string | Yes | Trigger price; required for `TAKE_STOP_LIMIT`, `TAKE_STOP_MARKET`, `TRIGGER_LIMIT`, `TRIGGER_MARKET` types |
| timeInForce | string | No | Time in force: `GTC` / `IOC` / `FOK` / `PostOnly`; required for `LIMIT`, default `GTC` |
| newClientOrderId | string | No | Only letters, numbers and _,Customized order ID for users, with a limit of characters from 1 to 40. Different orders can|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| symbol | string | Trading pair |
| orderId | long | System order ID |
| transactTime | long | Transaction timestamp (milliseconds) |
| price | string | Order price |
| origQty | string | Order quantity |
| executedQty | string | Filled quantity |
| cummulativeQuoteQty | string | Cumulative filled amount (quote asset) |
| status | string | Order status |
| type | string | Order type |
| side | string | Side |
| clientOrderID | string | Custom order ID |

---

### POST /openApi/spot/v1/trade/batchOrders — Batch Place Orders (up to 5)

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| data | array | Yes | Array of order objects |
| sync | bool | No | sync=false (default false if not filled in): parallel ordering (but all orders need to have the same symbol/side/type), |

Each order object fields: `symbol`, `side`, `type`, `quantity`, `quoteOrderQty`, `price`, `stopPrice`, `timeInForce`, `newClientOrderId`.

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| orders | array | Order result list; each entry has the same structure as the Place Order response |

---

## Cancel Order

### POST /openApi/spot/v1/trade/cancel — Cancel Single Order

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair |
| orderId | long | No | Order ID |
| clientOrderID | string | No | Customized order ID for users, with a limit of characters from 1 to 40. Different orders cannot use the same clientOrder|
| cancelRestrictions | string | No | Restrict cancellation by status: `NEW` / `PENDING` / `PARTIALLY_FILLED` |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| symbol | string | Trading pair |
| orderId | long | System order ID |
| price | string | Order price |
| origQty | string | Order quantity |
| executedQty | string | Filled quantity |
| cummulativeQuoteQty | string | Cumulative filled amount |
| status | string | Order status (after cancellation: `CANCELED`) |
| type | string | Order type |
| side | string | Side |
| clientOrderID | string | Custom order ID |

---

### POST /openApi/spot/v1/trade/cancelOrders — Batch Cancel Orders

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair |
| orderIds | string | Yes | Order Ids: for example:orderIds=id1,id2,id3 |
| clientOrderIDs | string | No | Custom order IDs, for example: clientOrderIDs=id1,id2,id3 |
| process | int | No | 0 or 1, default 0,if process=1,will handle valid orderIds partially, and return invalid orderIds in fails list, if proce|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| orders | array | Cancel result list; each entry has the same structure as the Cancel Single Order response |

---

### POST /openApi/spot/v1/trade/cancelOpenOrders — Cancel All Open Orders for a Trading Pair

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | No | Trading pair; if omitted, cancels all open orders across all pairs |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| orders | array | List of cancelled orders; each entry has the same structure as the Cancel Single Order response |

---

### POST /openApi/spot/v1/trade/cancelAllAfter — Cancel All After (Kill Switch)

Automatically cancels all open orders after a specified timeout. Prevents residual positions after program errors by continuously sending heartbeat requests to reset the countdown.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| type | string | Yes | Request type: ACTIVATE-Activate, CLOSE-Close |
| timeOut | long | Yes | Timeout duration (seconds); required when `type=ACTIVATE`; range 10–120 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| triggerTime | long | Timestamp (ms) when auto-cancel will trigger; `0` when closed |

---

### POST /openApi/spot/v1/trade/order/cancelReplace — Cancel and Replace Order

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | The trading pair, for example: BTC-USDT, please use uppercase letters |
| cancelOrderId | long | No | The ID of the order to be canceled |
| cancelRestrictions | string | No | Restrict cancellation by status: `NEW` / `PENDING` / `PARTIALLY_FILLED` |
| side | string | Yes | New order side: `BUY` / `SELL` |
| type | string | Yes | MARKET/LIMIT/TAKE_STOP_LIMIT/TAKE_STOP_MARKET/TRIGGER_LIMIT/TRIGGER_MARKET |
| quantity | float64 | No | New order quantity |
| quoteOrderQty | float64 | No | New order amount (MARKET BUY) |
| price | float64 | No | New order price |
| stopPrice | string | Yes | Trigger price used for TAKE_STOP_LIMIT, TAKE_STOP_MARKET, TRIGGER_LIMIT, TRIGGER_MARKET order types. |
| newClientOrderId | string | No | Custom order ID consisting of letters, numbers, and _. Character length should be between 1-40. Different orders cannot |
| cancelClientOrderID | string | No | The user-defined ID of the order to be canceled, character length limit: 1-40, different orders cannot use the same clie|
| cancelReplaceMode | string | Yes | STOP_ON_FAILURE: If the cancel order fails, it will not continue to place a new order. ALLOW_FAILURE: Regardless of whet|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| cancelResult | string | Cancel result: `SUCCESS` / `FAILURE` |
| newOrderResult | string | New order result: `SUCCESS` / `FAILURE` |
| cancelResponse | object | Cancel response; same structure as Cancel Single Order response |
| newOrderResponse | object | New order response; same structure as Place Order response |

---

## Query Orders

### GET /openApi/spot/v1/trade/query — Query Single Order

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair |
| orderId | long | No | Order ID |
| clientOrderID | string | No | Customized order ID for users, with a limit of characters from 1 to 40. Different orders cannot use the same clientOrder|

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| symbol | string | Trading pair |
| orderId | long | System order ID |
| price | string | Order price |
| origQty | string | Order quantity |
| executedQty | string | Filled quantity |
| cummulativeQuoteQty | string | Cumulative filled amount |
| status | string | Order status: `PENDING` / `NEW` / `PARTIALLY_FILLED` / `FILLED` / `CANCELED` / `FAILED` |
| type | string | Order type |
| side | string | Side |
| time | long | Order placement time (milliseconds) |
| updateTime | long | Last update time (milliseconds) |
| origQuoteOrderQty | string | Original order amount (quote asset) |
| fee | string | Fee amount |
| feeAsset | string | Fee asset |
| clientOrderID | string | Custom order ID |
| stopPrice | string | Trigger price |

---

### GET /openApi/spot/v1/trade/openOrders — Query Current Open Orders

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | No | Trading pair; if omitted, returns all open orders across all pairs |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| orders | array | Open order list; each entry has the same structure as the Query Single Order response |

---

### GET /openApi/spot/v1/trade/historyOrders — Query Order History

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | No | Trading pair |
| orderId | long | No | If orderId is set, orders >= orderId. Otherwise, the most recent orders will be returned. |
| startTime | long | No | Start timestamp (milliseconds) |
| endTime | long | No | End timestamp, Unit: ms |
| pageIndex | int | No | Page number, starting from 1; default 1 |
| pageSize | int | No | Page size, must >0,Max 100,If not specified, it defaults to 100. Restriction: pageIndex * pageSize <= 10,000. |
| status | string | No | status: FILLED (fully filled) CANCELED: (canceled) FAILED: (failed) |
| type | string | No | order type: MARKET/LIMIT/TAKE_STOP_LIMIT/TAKE_STOP_MARKET/TRIGGER_LIMIT/TRIGGER_MARKET |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| orders | array | Historical order list; each entry has the same structure as the Query Single Order response |
| total | int | Total record count |

---

### GET /openApi/spot/v1/trade/myTrades — Query Trade Fills

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, e.g. BTC-USDT, please use uppercase letters |
| orderId | long | No | Filter by order ID |
| startTime | long | No | Start timestamp (milliseconds) |
| endTime | long | No | End timestamp (milliseconds) |
| fromId | long | No | Starting trade ID. By default, the latest trade will be retrieved |
| limit | int | No | Number of results; default 500, max 1000 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| fills | array | Trade fill list |
| fills[].symbol | string | Trading pair |
| fills[].id | long | Fill ID |
| fills[].orderId | long | Order ID |
| fills[].price | string | Fill price |
| fills[].qty | string | Fill quantity |
| fills[].quoteQty | string | Fill amount (quote asset) |
| fills[].commission | string | Fee amount |
| fills[].commissionAsset | string | Fee asset |
| fills[].time | long | Fill time (milliseconds) |
| fills[].isBuyer | bool | Whether the user is the buyer |
| fills[].isMaker | bool | Whether the order is a maker order |

---

### GET /openApi/spot/v1/user/commissionRate — Query Commission Rate

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, e.g. BTC-USDT, please use uppercase letters |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| symbol | string | Trading pair |
| makerCommissionRate | string | Maker commission rate (e.g. `0.001` = 0.1%) |
| takerCommissionRate | string | Taker commission rate |

---

## OCO Orders

OCO (One-Cancels-the-Other) places a limit order and a stop-limit order simultaneously; when one is filled or triggered, the other is automatically cancelled.

### POST /openApi/spot/v1/oco/order — Create OCO Order

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, e.g., BTC-USDT, please use uppercase letters |
| side | string | Yes | Side: `BUY` / `SELL` |
| quantity | float64 | Yes | Order quantity (base asset) |
| limitPrice | float64 | Yes | Limit order execution price |
| triggerPrice | float64 | Yes | Stop-limit order trigger price |
| orderPrice | float64 | Yes | Stop-limit order execution price after trigger |
| listClientOrderId | string | No | Custom unique ID for the entire Order List, only supports numeric strings, e.g., "123456" |
| aboveClientOrderId | string | No | Custom order ID for the above order |
| belowClientOrderId | string | No | Custom order ID for the below order |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| orderListId | long | OCO group ID |
| contingencyType | string | Contingency type (`OCO`) |
| listStatusType | string | OCO group status |
| listOrderStatus | string | OCO group order status |
| transactionTime | long | Creation time (milliseconds) |
| symbol | string | Trading pair |
| orders | array | Order pair; each entry contains `symbol`, `orderId`, `clientOrderId` |
| orderReports | array | Detailed order info; each entry has the same structure as the Place Order response |

---

### POST /openApi/spot/v1/oco/cancel — Cancel OCO Order

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| orderId | string | No | The order ID of the limit order or the stop-limit order. Either orderId or clientOrderId must be provided. |
| clientOrderId | string | No | The User-defined order ID of the limit order or the stop-limit order |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| orderListId | long | OCO group ID |
| contingencyType | string | Contingency type |
| listStatusType | string | OCO group status |
| listOrderStatus | string | Order status (`ALL_DONE`) |
| transactionTime | long | Cancellation time (milliseconds) |
| symbol | string | Trading pair |
| orders | array | Order pair list |
| orderReports | array | Detailed cancellation info |

---

### GET /openApi/spot/v1/oco/orderList — Query OCO Order Details

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| orderListId | string | No | OCO group ID; at least one of `orderListId` or `listClientOrderId` required |
| clientOrderId | string | No | Custom order ID |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| orderListId | long | OCO group ID |
| contingencyType | string | Contingency type |
| listStatusType | string | List status |
| listOrderStatus | string | Order status |
| listClientOrderId | string | OCO group custom ID |
| transactionTime | long | Creation time (milliseconds) |
| symbol | string | Trading pair |
| orders | array | Order pair list, containing `orderId`, `clientOrderId` |

---

### GET /openApi/spot/v1/oco/openOrderList — Query All Open OCO Orders

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| pageIndex | int64 | Yes | Page number (1-based) |
| pageSize | int64 | Yes | Number of items per page |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| ocoOrders | array | OCO order list; each entry has the same structure as the Query OCO Order Details response |

---

### GET /openApi/spot/v1/oco/historyOrderList — Query Historical OCO Orders

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| startTime | long | No | Start timestamp (milliseconds) |
| endTime | long | No | End timestamp (milliseconds) |
| pageIndex | int | Yes | Page number, starting from 1; default 1 |
| pageSize | int | Yes | Items per page; default 100, max 1000 |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| ocoOrders | array | Historical OCO order list; each entry has the same structure as the Query OCO Order Details response |
| total | int | Total record count |