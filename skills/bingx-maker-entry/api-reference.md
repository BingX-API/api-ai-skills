# API Endpoints

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md)

---

## 1. Get Order Book Depth

`GET /openApi/swap/v2/quote/depth`

Rate limit: 1/s per IP.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, e.g. BTC-USDT |
| limit | int | No | Depth levels, default 20, max 1000 |

**Response data:** `{ bids: [[price, qty]], asks: [[price, qty]] }`

---

## 2. Place Order

`POST /openApi/swap/v2/trade/order`

Rate limit: 2/s per UID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair |
| side | string | Yes | BUY or SELL |
| type | string | Yes | LIMIT |
| price | float | Yes | Limit price |
| quantity | float | Yes | Order quantity |

**Response data:** `{ orderId, symbol, status, price, quantity }`

---

## 3. Cancel Order

`DELETE /openApi/swap/v2/trade/order`

Rate limit: 2/s per UID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair |
| orderId | int64 | Yes | Order ID to cancel |

**Response data:** `{ orderId, status }`

---

# Maker vs Taker Fee Comparison

## BingX Perpetual Futures Fee Rates

| Type | Rate | Description |
|------|------|-------------|
| Maker | 0.020% | Limit order that provides liquidity |
| Taker | 0.050% | Market order that consumes liquidity |
| Savings | 0.030% | Fee difference saved per trade |

## Fee Savings Examples

| Trade Amount | Maker Fee | Taker Fee | Savings |
|-------------|-----------|-----------|---------|
| 1,000 USDT | $0.20 | $0.50 | $0.30 |
| 5,000 USDT | $1.00 | $2.50 | $1.50 |
| 10,000 USDT | $2.00 | $5.00 | $3.00 |
| 50,000 USDT | $10.00 | $25.00 | $15.00 |

## When to Use Maker Limit Orders

**Good scenarios:**
- Price is near support/resistance levels, waiting for a pullback entry
- Large trade size where market impact cost is significant
- Ranging market where price oscillates within a zone

**Not suitable:**
- Strong trending breakout where immediate fill is needed
- Stop-loss / take-profit orders where guaranteed fill is required (use market orders)
- Very illiquid order books (wide spread makes limit fills unlikely)

## Dynamic Adjustment Rules

| Trigger Condition | Action |
|------------------|--------|
| Price moves > 0.3% in favorable direction | No adjustment, wait for fill |
| Price moves > 0.3% in unfavorable direction | Cancel and re-place near new best price |
| Order is > 1% away from best bid/ask | Cancel, recalculate entry levels |
