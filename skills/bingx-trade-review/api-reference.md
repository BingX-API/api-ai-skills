# API Endpoints

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md)

---

## 1. Get All Orders

`GET /openApi/swap/v2/trade/allOrders`

Rate limit: 1/s per UID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, e.g. BTC-USDT |
| limit | int | No | Max results, default 500, max 1000 |
| startTime | int64 | No | Start timestamp in milliseconds |
| endTime | int64 | No | End timestamp in milliseconds |

**Response data:** Array of order objects with `{ orderId, symbol, side, type, price, quantity, status, realizedPnl, fee }`

---

## 2. Get All Fill Orders

`GET /openApi/swap/v2/trade/allFillOrders`

Rate limit: 1/s per UID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, e.g. BTC-USDT |
| limit | int | No | Max results, default 500, max 1000 |
| startTime | int64 | No | Start timestamp in milliseconds |
| endTime | int64 | No | End timestamp in milliseconds |

**Response data:** Array of fill objects with `{ tradeId, orderId, symbol, side, price, quantity, realizedPnl, fee, closeTime }`

---

# Statistics Metric Definitions

| Metric | Calculation | Description |
|--------|------------|-------------|
| total_trades | count | Total number of trades |
| win_rate | winning trades / total trades × 100% | Win rate |
| total_pnl | sum(realizedPnl) | Total profit and loss (USDT) |
| avg_pnl | total_pnl / total_trades | Average PnL per trade |
| max_win | max(pnl) | Largest single trade profit |
| max_loss | min(pnl) | Largest single trade loss |
| profit_factor | total profit / abs(total loss) | Profit factor; >1 means net profitable |
| avg_hold_time | avg(close time - open time) | Average position hold duration |
| max_drawdown | max drawdown of cumulative PnL curve | Negative value; larger absolute = higher risk |
| sharpe_ratio | avg PnL per trade / std deviation | Risk-adjusted return; >1 is good |
| long_win_rate | long winning trades / total long trades | Win rate for long positions |
| short_win_rate | short winning trades / total short trades | Win rate for short positions |
| best_symbol | Symbol with highest total profit | Grouped by trading pair |
| worst_symbol | Symbol with highest total loss | Grouped by trading pair |
| total_fees | sum(fee) | Total fees paid |

---

## Metric Benchmarks

| Metric | Excellent | Good | Needs Improvement |
|--------|-----------|------|--------------------|
| Win Rate | > 60% | 50–60% | < 50% |
| Profit Factor | > 2.0 | 1.5–2.0 | < 1.5 |
| Sharpe Ratio | > 2.0 | 1.0–2.0 | < 1.0 |
| Max Drawdown | < 5% | 5–15% | > 15% |

---

## Chart Descriptions

| Chart | Filename | Purpose |
|-------|----------|---------|
| PnL Curve | pnl_curve.png | Observe overall equity curve trend and drawdowns |
| Win/Loss Distribution | win_loss_dist.png | Visualize PnL distribution and identify large losses |
| Symbol Breakdown | symbol_breakdown.png | Identify best and worst performing symbols |
| Hold Time Distribution | hold_time_dist.png | Determine optimal trading timeframe |
| Long vs Short | long_short_compare.png | Compare performance between long and short trades |
| Tag Analysis | tag_breakdown.png | Evaluate actual performance of each strategy tag |
