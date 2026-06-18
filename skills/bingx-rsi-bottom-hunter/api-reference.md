# API Endpoints

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md)

---

## 1. Get Klines

`GET /openApi/swap/v3/quote/klines`

Rate limit: 1/s per IP.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, e.g. BTC-USDT |
| interval | string | Yes | Kline interval (1h recommended for RSI) |
| limit | int | No | Number of candles, default 500 |

**Response data:** Array of `[openTime, open, high, low, close, volume, closeTime]`

---

## 2. Place Order

`POST /openApi/swap/v2/trade/order`

Rate limit: 2/s per UID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair |
| side | string | Yes | BUY or SELL |
| type | string | Yes | MARKET |
| quantity | float | Yes | Order quantity |

**Response data:** `{ orderId, symbol, status, avgPrice }`

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

# Default Parameters & Tuning Guide

## Default Parameters

| Parameter | Default | Suggested Range | Description |
|-----------|---------|----------------|-------------|
| symbol | BTC-USDT | Any perpetual pair | Trading pair |
| interval | 1h | 15m / 1h / 4h | Kline interval; larger = more reliable but slower signals |
| rsi_period | 14 | 7–21 | RSI calculation period; 14 is the industry standard |
| rsi_buy | 30 | 20–35 | Buy trigger threshold; lower = fewer but more reliable signals |
| rsi_sell | 70 | 65–80 | Take-profit reference threshold |
| stop_loss_pct | 3% | 2%–8% | Stop-loss percentage; widen for high-volatility assets |
| take_profit_pct | 5% | 3%–15% | Take-profit percentage |
| leverage | 1x | 1x–5x | Leverage multiplier; 1x recommended for beginners |
| monitor_interval | 5min | 1–15min | Polling frequency |

---

## Signal Trigger Conditions (all must be met)

1. Current RSI < rsi_buy
2. RSI on the previous candle also < rsi_buy (consecutive oversold)
3. Current candle close > open (reversal signal)

---

## Tuning Presets

### Aggressive (more signals)
```
rsi_buy = 35, stop_loss_pct = 2%, take_profit_pct = 3%, interval = 15m
```

### Balanced (default, recommended for beginners)
```
rsi_buy = 30, stop_loss_pct = 3%, take_profit_pct = 5%, interval = 1h
```

### Conservative (high-confidence only)
```
rsi_buy = 25, stop_loss_pct = 5%, take_profit_pct = 10%, interval = 4h
```

---

## Important Notes

- **Avoid in sustained downtrends**: RSI can stay in oversold territory for extended periods, triggering repeated signals and losses
- **High leverage risk**: when leverage > 3x, reduce stop-loss percentage accordingly
- **monitor mode fires once**: the strategy stops automatically after one execution to prevent repeated entries
