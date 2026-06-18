# API Endpoints

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md)

---

## 1. Get Klines

`GET /openApi/swap/v3/quote/klines`

Rate limit: 1/s per IP.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, e.g. BTC-USDT |
| interval | string | Yes | Kline interval (4h recommended for ATR) |
| limit | int | No | Number of candles, default 500 |

**Response data:** Array of `[openTime, open, high, low, close, volume, closeTime]`

---

## 2. Place Conditional Order (SL/TP)

`POST /openApi/swap/v2/trade/order`

Rate limit: 2/s per UID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair |
| side | string | Yes | BUY or SELL |
| type | string | Yes | STOP / TAKE_PROFIT / TRAILING_STOP_MARKET |
| stopPrice | float | Yes | Trigger price |
| quantity | float | Yes | Order quantity |

**Response data:** `{ orderId, symbol, type, stopPrice, status }`

---

## 3. Cancel Conditional Order

`DELETE /openApi/swap/v2/trade/order`

Rate limit: 2/s per UID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair |
| orderId | int64 | Yes | Order ID to cancel |

**Response data:** `{ orderId, status }`

---

# SL/TP Strategy Reference

## Stop-Loss Strategies

| Strategy | Parameter | Use Case | Characteristics |
|----------|-----------|----------|----------------|
| ATR × 1.0 | atr_multiplier=1.0 | Scalping, high-frequency | Tight stop, easily stopped out, small loss |
| ATR × 1.5 | atr_multiplier=1.5 | Default, intraday swing | Balanced tolerance for volatility vs loss |
| ATR × 2.0 | atr_multiplier=2.0 | Larger timeframe trend | Wide stop, gives price more room |
| ATR × 3.0 | atr_multiplier=3.0 | Daily timeframe | Very wide, only guards against extreme moves |
| Structure Stop | strategy=structure | Trending market | Based on prior swing low/high, aligned with market structure |
| Volatility Stop | strategy=volatility | High-volatility market | Width adjusts dynamically with volatility |
| Fixed Percentage | strategy=fixed_pct | User-specified | Simple and direct, independent of volatility |

---

## Take-Profit Modes

| Mode | Description | Orders Placed | Use Case |
|------|-------------|---------------|----------|
| ratio | Fixed R:R single take-profit | 1 conditional order | Simple and clear, recommended for beginners |
| levels | Partial TP (3 levels: 40%/30%/30%) | 3 conditional orders | Balance locking profits and letting profits run |
| trailing | Full position trailing stop | 1 Trailing Stop | Strong trending market, maximizing gains |
| breakeven | Move SL to break-even after TP1 fills | 2 conditional orders | Reduce risk, guarantee no loss |
| hybrid | Partial TP + Trailing Stop on remainder | 2 conditional + 1 Trailing | Most flexible, for experienced traders |

---

## Default Partial Take-Profit Plan

| Level | Price | Close % | Logic |
|-------|-------|---------|-------|
| TP1 | Entry ± 1R | 40% | Lock in initial profits |
| TP2 | Entry ± 2R | 30% | Main target |
| TP3 | Entry ± 3R | 30% | Let profits run |

R = |entry price − stop-loss price| (1 unit of risk)

---

## Trailing Stop Parameters

| Parameter | Calculation | Description |
|-----------|-------------|-------------|
| callback_rate | ATR(14) / current price × 100% | Callback rate matched to volatility |
| activation_price | TP1 price level | Trailing starts when this price is reached |

---

## Quick Selection Guide

**Beginner**: ATR × 1.5 stop-loss + levels partial take-profit

**Scalping**: ATR × 1.0 stop-loss + trailing take-profit

**Trend following**: Structure stop-loss + hybrid (partial + Trailing)

**Conservative**: ATR × 2.0 stop-loss + breakeven mechanism
