# BingX Trading Plan API Reference

## Internal Lindorm Query

Endpoint: `POST /api/lindorm/v1/ai/kline/query`

Rate limit: internal endpoint policy; keep requests conservative and avoid polling.

**Base URL:** `https://ox-bigdata-api.houtai.io`

**Auth:** Requires platform-provided `access_token` and `proxy_user` headers. Never hard-code credentials in skill files.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| indicatorType | string | Yes | Lindorm lab code |
| symbol | string | No | Compact symbol or coin symbol, for example `BTCUSDT` or `BTC` |
| interval | string | No | Data interval or heatmap range. If the requested value returns no rows, fall back to the indicator's synced default |
| startTime | int64 | No | Start timestamp in milliseconds |
| endTime | int64 | No | End timestamp in milliseconds |
| offset | string | No | Pagination offset, default `0` |
| size | string | No | Number of rows |

**Response data:** rows with `extraData` as a JSON string.

Known interval behavior:

| Indicator | Default / validated interval | Notes |
|-----------|------------------------------|-------|
| `global_ls_ratio` | `4h`, `1d` | Supports `symbol`, for example `BTCUSDT` |
| `top_position_ls_ratio` | `4h` | Validated `5m`, `15m`, `30m`, `1h`, `6h`, `8h`, `12h`, `1d`, and `1w` currently return empty data |
| `liquidation_aggregated_heatmap` | `3d` | Current available data is coin-level aggregated data. Use coin symbol such as `BTC` |

```json
{
  "code": 0,
  "data": [
    {
      "rowKey": "top_position_ls_ratio#4h#Binance#BTCUSDT#1784534400000",
      "indicatorType": "top_position_ls_ratio",
      "intervalVal": "4h",
      "exchange": "Binance",
      "symbol": "BTCUSDT",
      "ts": 1784534400000,
      "dataSource": "coinglass",
      "extraData": "{\"time\":1784534400000,\"top_position_long_percent\":60.62,\"top_position_short_percent\":39.38,\"top_position_long_short_ratio\":1.54}"
    }
  ]
}
```

## Global Account Long-Short Ratio

Endpoint: `POST /api/lindorm/v1/ai/kline/query`

Rate limit: internal endpoint policy.

Use `indicatorType=global_ls_ratio`.

Original upstream reference: `/api/futures/global-long-short-account-ratio/history`

**Response data:** `global_account_long_percent`, `global_account_short_percent`, `global_account_long_short_ratio`, `time`.

## Top Account Long-Short Ratio

Endpoint: `POST /api/lindorm/v1/ai/kline/query`

Rate limit: internal endpoint policy.

Use `indicatorType=top_ls_ratio`.

Original upstream reference: `/api/futures/top-long-short-account-ratio/history`

**Response data:** `top_account_long_percent`, `top_account_short_percent`, `top_account_long_short_ratio`, `time`.

Important: this is top account long-short ratio, not top position long-short ratio.

## Top Position Long-Short Ratio

Endpoint: `POST /api/lindorm/v1/ai/kline/query`

Rate limit: internal endpoint policy.

Use `indicatorType=top_position_ls_ratio`.

Original upstream reference: `/api/futures/top-long-short-position-ratio/history`

**Response data:** expected fields are `top_position_long_percent`, `top_position_short_percent`, `top_position_long_short_ratio`, `time`.

## Liquidation Heatmap

Endpoint: `POST /api/lindorm/v1/ai/kline/query`

Rate limit: internal endpoint policy.

Use `indicatorType=liquidation_aggregated_heatmap`.

Current status: available data is coin-level aggregated data. Convert the compact pair to a coin symbol such as `BTC` and query with `interval=3d`. Pair-level liquidation structure is not available.

Original upstream references:

| Upstream API | Scope |
|--------------|-------|
| `/api/futures/liquidation/aggregated-heatmap/model3` | Coin aggregated heatmap |
| `/api/futures/liquidation/heatmap/model3` | Pair heatmap |

**Response data:** rows with `extraData` fields including `time`, `open`, `high`, `low`, `close`, `volume`, `x_idx`, `y_idx`, `price_level`, and `intensity`.

Example row:

```json
{
  "indicatorType": "liquidation_aggregated_heatmap",
  "intervalVal": "3d",
  "exchange": "DEFAULT",
  "symbol": "BTC",
  "ts": 1784627100000,
  "dataSource": "coinglass",
  "extraData": "{\"time\":1784627100000,\"open\":\"66272.2\",\"high\":\"66281.8\",\"low\":\"66264.3\",\"close\":\"66281.7\",\"volume\":\"4845699.8159\",\"x_idx\":863,\"y_idx\":384,\"price_level\":79554.9,\"intensity\":258806.0}"
}
```

Parsing rule:

| Field | Usage |
|-------|-------|
| `price_level` | Liquidation price level |
| `intensity` | Liquidation pressure or amount proxy |
| latest `close` | Current price fallback |

Price levels above current price are `liqAbove`; price levels below current price are `liqBelow`.

## Funding Rate

`GET /openApi/swap/v2/quote/premiumIndex`

Rate limit: 1/s per IP.

**Base URL:** `https://open-api.bingx.com`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | No | Trading pair, for example `BTC-USDT` |

**Response data:** funding rate, mark price, index price, and next funding time.

## Klines

`GET /openApi/swap/v3/quote/klines`

Rate limit: 1/s per IP.

**Base URL:** `https://open-api.bingx.com`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, for example `BTC-USDT` |
| interval | string | Yes | Kline interval |
| limit | int | No | Number of candles |
| startTime | int64 | No | Start timestamp in milliseconds |
| endTime | int64 | No | End timestamp in milliseconds |

**Response data:** array of `[openTime, open, high, low, close, volume, closeTime]`.

## Depth

`GET /openApi/swap/v2/quote/depth`

Rate limit: 1/s per IP.

**Base URL:** `https://open-api.bingx.com`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, for example `BTC-USDT` |
| limit | int | No | Depth limit |

**Response data:** bid and ask levels.
