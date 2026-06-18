# API Endpoints

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** HMAC-SHA256 — see [`references/authentication.md`](../references/authentication.md)

---

## 1. Get Klines

`GET /openApi/swap/v3/quote/klines`

Rate limit: 1/s per IP.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, e.g. BTC-USDT |
| interval | string | Yes | Kline interval (1m/5m/15m/1h/4h/1d etc.) |
| limit | int | No | Number of candles, default 500, max 1440 |

**Response data:** Array of `[openTime, open, high, low, close, volume, closeTime]`

---

## 2. Get Premium Index & Funding Rate

`GET /openApi/swap/v2/quote/premiumIndex`

Rate limit: 1/s per IP.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | No | Trading pair; returns all if omitted |

**Response data:** `{ fundingRate, markPrice, nextFundingTime }`

---

## 3. Get Open Interest

`GET /openApi/swap/v2/quote/openInterest`

Rate limit: 1/s per IP.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Trading pair, e.g. BTC-USDT |

**Response data:** `{ openInterest, symbol }`

---

# 78 Indicator Quick Reference

> Source: pandas-ta-classic. Reference for Agent when interpreting indicator values.

## Trend

| Indicator | Column Prefix | Description | Bullish Signal | Bearish Signal |
|-----------|--------------|-------------|----------------|----------------|
| EMA | EMA_{period} | Exponential Moving Average | 7>25>99 bullish alignment | 7<25<99 bearish alignment |
| SMA | SMA_{period} | Simple Moving Average | Price above MA | Price below MA |
| WMA | WMA_{period} | Weighted Moving Average | Same as EMA | Same as EMA |
| DEMA | DEMA_{period} | Double EMA | Same as EMA | Same as EMA |
| TEMA | TEMA_{period} | Triple EMA | Same as EMA | Same as EMA |
| HMA | HMA_{period} | Hull Moving Average | Turning up | Turning down |
| VWMA | VWMA_{period} | Volume-Weighted MA | Price above | Price below |
| ALMA | ALMA_{period} | Arnaud Legoux MA | Same as EMA | Same as EMA |
| Supertrend | SUPERT_ | Supertrend line | Direction=UP(+1) | Direction=DOWN(-1) |
| Ichimoku | ISA_ / ISB_ | Ichimoku Cloud | Price above cloud + conversion>base | Price below cloud |
| PSAR | PSARl_ / PSARs_ | Parabolic SAR | Price above SAR | Price below SAR |
| ADX | ADX_ | Average Directional Index | >25 trending | <20 no trend |
| DMP/DMN | DMP_ / DMN_ | Directional Movement | DMP>DMN | DMP<DMN |
| Aroon | AROONU_ / AROOND_ | Aroon | Up>70, Down<30 | Up<30, Down>70 |
| VHF | VHF_ | Vertical Horizontal Filter | High=trending | Low=ranging |
| Vortex | VTXP_ / VTXM_ | Vortex Indicator | VTXP>VTXM | VTXP<VTXM |
| QStick | QS_ | QStick | >0 bullish candles | <0 bearish candles |
| CKSP | CKSPl_ / CKSPs_ | Chandelier KSP | Above long stop | Below short stop |

## Momentum

| Indicator | Column Prefix | Description | Overbought | Oversold |
|-----------|--------------|-------------|------------|---------|
| RSI | RSI_ | Relative Strength Index | >70 | <30 |
| MACD | MACD_ / MACDs_ / MACDh_ | MACD | Histogram >0 and expanding | Histogram <0 and expanding |
| StochRSI | STOCHRSIk_ / STOCHRSId_ | Stochastic RSI | K>80 | K<20 |
| Stoch | STOCHk_ / STOCHd_ | Stochastic Oscillator | K>80 | K<20 |
| KDJ | Derived from Stoch | K/D/J | J>100 | J<0 |
| CCI | CCI_ | Commodity Channel Index | >100 | <-100 |
| MFI | MFI_ | Money Flow Index | >80 | <20 |
| Williams %R | WILLR_ | Williams %R | >-20 | <-80 |
| AO | AO_ | Awesome Oscillator | >0 crossover | <0 crossover |
| APO | APO_ | Absolute Price Oscillator | >0 | <0 |
| PPO | PPO_ | Percentage Price Oscillator | >0 | <0 |
| DPO | DPO_ | Detrended Price Oscillator | >0 | <0 |
| TSI | TSI_ | True Strength Index | >0 crossover | <0 crossover |
| CMO | CMO_ | Chande Momentum Oscillator | >50 | <-50 |
| Fisher | FISHERT_ | Fisher Transform | Bullish cross | Bearish cross |
| TRIX | TRIX_ | Triple Smoothed EMA Rate | >0 | <0 |
| RVGI | RVGI_ | Relative Vigor Index | >0 | <0 |
| Slope | SLOPE_ | Slope | >0 | <0 |
| Squeeze | SQZ_ | Squeeze Momentum | Release + positive | Release + negative |
| SqueezePro | SQZPRO_ | Squeeze Pro | Same as above | Same as above |

## Volatility

| Indicator | Column Prefix | Description | Signal |
|-----------|--------------|-------------|--------|
| Bollinger Bands | BBU_ / BBM_ / BBL_ | Bollinger Bands | %B>1 overbought, %B<0 oversold |
| ATR | ATR_ | Average True Range | Used for stop-loss calculation |
| Keltner Channel | KCUe_ / KCLe_ | Keltner Channel | Breakout above upper band is bullish |
| Donchian | DCU_ / DCL_ | Donchian Channel | Price making new highs |
| BBANDS Width | BBB_ | Bollinger Band Width | Narrowing=consolidation, expanding=breakout |
| Massi | MASSI_ | Mass Index | >27 then <26.5 reversal signal |
| NATR | NATR_ | Normalized ATR | High value=high volatility |
| HiLo | HiLo_ | HiLo Channel | Same as Keltner |
| PDIST | PDIST_ | Price Distance | High value=large amplitude |
| RVI | RVI_ | Relative Volatility Index | >0 bullish |
| Aberration | ABER_ZG | Aberration | Degree of deviation from mean |

## Volume

| Indicator | Column Prefix | Description | Bullish Signal |
|-----------|--------------|-------------|----------------|
| OBV | OBV | On-Balance Volume | Moving in same direction as price |
| CMF | CMF_ | Chaikin Money Flow | >0.1 |
| VWAP | VWAP | Volume-Weighted Avg Price | Price above VWAP |
| AD | AD | Accumulation/Distribution | Rising |
| ADOSC | ADOSC_ | A/D Oscillator | >0 |
| NVI | NVI_ | Negative Volume Index | Price above NVI |
| PVI | PVI_ | Positive Volume Index | Same as NVI |
| PVO | PVO_ | Volume Percentage Oscillator | >0 |
| EOM | EOM_ | Ease of Movement | Crosses above 0 |
| PVOL | PVOL_ | Price Volume | Positive value |
| VP | — | Volume Profile | Support near POC |

## Statistical / Other

| Indicator | Description |
|-----------|-------------|
| ENTROPY_ | Price entropy; higher = more disordered |
| KURTOSIS_ | Kurtosis |
| SKEW_ | Skewness |
| STDEV_ | Standard deviation |
| VARIANCE_ | Variance |
| ZSCORE_ | Z-score; >2 overbought, <-2 oversold |
| QUANTILE_ | Quantile |
| MAD_ | Mean Absolute Deviation |
| MEDIAN_ | Median |
| MIDPOINT_ | Midpoint |
| MIDPRICE_ | Mid price |
| OHLC4_ | (O+H+L+C)/4 |
| HL2_ | (H+L)/2 |
| HLC3_ | (H+L+C)/3 |
| HLCC4_ | (H+L+C+C)/4 |

---

# 62 Candlestick Pattern Quick Reference

> Patterns covered by pandas-ta `cdl_pattern(name="all")`. Reference for Agent interpretation.
> Return values: positive = bullish, negative = bearish, 0 = no pattern.

## Bullish Reversal Patterns

| Pattern | Context | Reliability |
|---------|---------|-------------|
| Hammer | End of downtrend | ★★★ |
| Inverted Hammer | End of downtrend | ★★ |
| Bullish Engulfing | End of downtrend | ★★★★ |
| Piercing Line | End of downtrend | ★★★ |
| Morning Star | End of downtrend (3 candles) | ★★★★ |
| Morning Doji Star | End of downtrend (3 candles) | ★★★★ |
| Bullish Harami | Mid-downtrend | ★★ |
| Bullish Harami Cross | Mid-downtrend | ★★★ |
| Three White Soldiers | End of downtrend / consolidation | ★★★★ |
| Rising Three Methods | In uptrend | ★★★ |
| Dragonfly Doji | End of downtrend | ★★★ |
| Belt Hold (Bull) | End of downtrend | ★★ |
| Breakaway (Bull) | End of downtrend (5 candles) | ★★★ |
| Concealing Baby Swallow | End of downtrend (4 candles) | ★★★ |
| Ladder Bottom | End of downtrend (5 candles) | ★★★ |
| Matching Low | End of downtrend | ★★ |
| Mat Hold | In uptrend | ★★★ |
| Three Inside Up | End of downtrend | ★★★ |
| Three Outside Up | End of downtrend | ★★★★ |
| Unique Three River | End of downtrend (3 candles) | ★★ |
| Upside Tasuki Gap | In uptrend | ★★★ |
| Upside Gap Two Crows | In uptrend | ★★ |
| Stick Sandwich | Mid-downtrend | ★★ |
| Homing Pigeon | Mid-downtrend | ★★ |
| Kicking (Bull) | Any | ★★★ |

## Bearish Reversal Patterns

| Pattern | Context | Reliability |
|---------|---------|-------------|
| Hanging Man | End of uptrend | ★★★ |
| Shooting Star | End of uptrend | ★★★ |
| Bearish Engulfing | End of uptrend | ★★★★ |
| Dark Cloud Cover | End of uptrend | ★★★ |
| Evening Star | End of uptrend (3 candles) | ★★★★ |
| Evening Doji Star | End of uptrend (3 candles) | ★★★★ |
| Bearish Harami | Mid-uptrend | ★★ |
| Bearish Harami Cross | Mid-uptrend | ★★★ |
| Three Black Crows | End of uptrend / consolidation | ★★★★ |
| Falling Three Methods | In downtrend | ★★★ |
| Gravestone Doji | End of uptrend | ★★★ |
| Belt Hold (Bear) | End of uptrend | ★★ |
| Advance Block | End of uptrend (3 candles) | ★★★ |
| Deliberation | End of uptrend (3 candles) | ★★★ |
| Identical Three Crows | End of uptrend (3 candles) | ★★★ |
| Three Inside Down | End of uptrend | ★★★ |
| Three Outside Down | End of uptrend | ★★★★ |
| Two Crows | End of uptrend (3 candles) | ★★★ |
| Upside Gap Two Crows | End of uptrend (3 candles) | ★★★ |
| Kicking (Bear) | Any | ★★★ |

## Neutral / Indecision Patterns

| Pattern | Description |
|---------|-------------|
| Doji | Open and close near equal, direction uncertain |
| Long Legged Doji | Long upper and lower shadows, high uncertainty |
| Dragonfly Doji | Long lower shadow, potentially bullish |
| Gravestone Doji | Long upper shadow, potentially bearish |
| Rickshaw Man | Similar to Long Legged Doji, high uncertainty |
| Spinning Top | Small body, balance between bulls and bears |
| High Wave | Very long upper and lower shadows, high volatility |
| Marubozu | No shadows, strong trend continuation |
| Inside | Previous candle contains current candle, awaiting breakout |
| On Neck | Rebound resistance |
| In Neck | Slight penetration, still bearish |
| Thrusting | Weaker than Piercing Line, bearish continuation |
| Separating Lines | Trend continuation |
| Tasuki Gap | Gap holds, trend continuation |
| Side-by-side White Lines | Uptrend continuation |
| Tri-Star | Three doji candles, important reversal warning |

## Usage Notes

1. **Pattern reliability depends on trend context**: reversal patterns at clear trend extremes are more reliable
2. **Confirm with volume**: breakout or reversal patterns accompanied by high volume are more valid
3. **Higher timeframes are more reliable**: daily > 4h > 1h
4. **pandas-ta return values**:
   - `100` = strong bullish
   - `200` = very strong bullish (e.g. Three White Soldiers)
   - `-100` = strong bearish
   - `-200` = very strong bearish (e.g. Three Black Crows)
