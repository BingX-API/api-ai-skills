# BingX Sentiment Dashboard API Reference

## Fear & Greed Index

`GET https://api.alternative.me/fng/`

Rate limit: public endpoint policy; keep requests conservative and avoid polling.

**Base URL:** `https://api.alternative.me`

**Auth:** No auth required.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | int | No | Number of records to return. Default is `10`; replace as needed |

**Response data:** latest and historical Fear & Greed entries.

| Field | Description |
|-------|-------------|
| name | Index name |
| data[].value | Fear & Greed Index value from 0 to 100 |
| data[].value_classification | Text label such as `Extreme Fear`, `Fear`, `Neutral`, `Greed`, or `Extreme Greed` |
| data[].timestamp | Unix timestamp in seconds |
| data[].time_until_update | Seconds until next update, present on the latest item |
| metadata.error | Error message when unavailable |

```json
{
  "name": "Fear and Greed Index",
  "data": [
    {
      "value": "24",
      "value_classification": "Extreme Fear",
      "timestamp": "1783296000",
      "time_until_update": "42048"
    }
  ],
  "metadata": {
    "error": null
  }
}
```

## Funding Rates

`GET /openApi/swap/v2/quote/premiumIndex`

Rate limit: 1/s per IP.

**Base URL:** `https://open-api.bingx.com`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | No | Trading pair, for example `BTC-USDT`. Omit to get all available symbols |

**Response data:** array of funding rate objects per symbol.

```json
{
  "data": [
    {
      "symbol": "BTC-USDT",
      "markPrice": "67500.00",
      "indexPrice": "67480.00",
      "lastFundingRate": "0.0001",
      "nextFundingTime": 1700000000000
    }
  ]
}
```

## Open Interest

`GET /openApi/swap/v2/quote/openInterest`

Rate limit: 1/s per IP.

**Base URL:** `https://open-api.bingx.com`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, for example `BTC-USDT` |

**Response data:** `{ symbol, openInterest, time }`.

```json
{
  "data": {
    "symbol": "BTC-USDT",
    "openInterest": "12345.67",
    "time": 1700000000000
  }
}
```

## Klines

`GET /openApi/swap/v3/quote/klines`

Rate limit: 1/s per IP.

**Base URL:** `https://open-api.bingx.com`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, for example `BTC-USDT` |
| interval | string | Yes | Kline interval: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w` |
| limit | int | No | Number of candles |
| startTime | int64 | No | Start timestamp in milliseconds |
| endTime | int64 | No | End timestamp in milliseconds |

**Response data:** array of `[openTime, open, high, low, close, volume, closeTime]`.

```json
{
  "data": [
    [1700000000000, "67000.00", "67500.00", "66800.00", "67300.00", "1234.56", 1700003600000]
  ]
}
```

# Sentiment Calculation Reference

## Composite Score Weights

| Dimension | Weight | Data Source | Current Status |
|-----------|--------|-------------|----------------|
| Fear & Greed Index | 30% | `https://api.alternative.me/fng/?limit={limit}` | Available |
| Funding Rate | 25% | `/openApi/swap/v2/quote/premiumIndex` | Available |
| Open Interest | 25% | `/openApi/swap/v2/quote/openInterest` | Available |
| AHR999 | 20% | Local BTC daily kline calculation | Available locally |

## Composite Sentiment Score Levels

| Score Range | Label | Meaning |
|-------------|-------|---------|
| +70 to +100 | EXTREME_GREED | Market overheated |
| +30 to +69 | GREED | Market running hot |
| -29 to +29 | NEUTRAL | Balanced |
| -69 to -30 | FEAR | Market cold |
| -100 to -70 | EXTREME_FEAR | Potential historical bottom |

## OI Anomaly Types

| Type | Condition | Interpretation |
|------|-----------|----------------|
| LONG_BUILDUP | OI surge and price up more than 3% | Longs building positions |
| SHORT_BUILDUP | OI surge and price down more than 3% | Shorts building positions |
| OI_SURGE | OI surge, direction unclear | Significant position buildup |
| OI_DROP | OI sudden drop | Position reduction |
| LIQUIDATION | OI sudden drop plus high price volatility | Suspected liquidation event |

OI change threshold: more than 15% triggers anomaly detection.

## Funding Rate Signals

| Scenario | Signal |
|----------|--------|
| Market average above +0.05% | Longs overheated, high cost to go long |
| More than 60% symbols positive | Market sentiment overheated |
| Market average below -0.05% | Shorts overheated, high cost to short |
| More than 60% symbols negative | Market panic warning |

## AHR999 Index Zones

| Value | Zone | Meaning |
|-------|------|---------|
| < 0.45 | Accumulation Zone | Price well below DCA cost, historical bottom signal |
| 0.45 - 1.2 | DCA Zone | Price reasonably low, suitable for regular DCA |
| 1.2 - 5.0 | Wait Zone | Price elevated, hold and observe |
| > 5.0 | Overheated Zone | Price far above estimate, consider reducing exposure |

**Formula:** `AHR999 = (current_price / 200d_dca_cost) * (current_price / exp_growth_value)`

`exp_growth_value = 10 ^ (5.84 * log10(days_since_genesis) - 17.01)`

BTC genesis date: 2009-01-03.
