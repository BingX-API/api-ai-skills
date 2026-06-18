"""
Multi-timeframe composite scoring module.
Can run standalone: python3 score.py --klines_15m '...' --klines_1h '...' --klines_4h '...' --klines_1d '...'
Can also be called internally by analyze.py.
"""
import pandas as pd
import pandas_ta_classic as ta
import json, argparse, sys
import numpy as np


WEIGHTS = {"15m": 0.15, "1h": 0.30, "4h": 0.35, "1d": 0.20}


def score_single(df: pd.DataFrame) -> dict:
    df.ta.strategy("All")

    def label(s):
        if s >= 80: return "STRONG_BULLISH"
        elif s >= 60: return "BULLISH"
        elif s >= 40: return "NEUTRAL"
        elif s >= 20: return "BEARISH"
        return "STRONG_BEARISH"

    # Trend
    ema7 = df.get("EMA_7", pd.Series([np.nan]*len(df))).iloc[-1]
    ema25 = df.get("EMA_25", pd.Series([np.nan]*len(df))).iloc[-1]
    ema99 = df.get("EMA_99", pd.Series([np.nan]*len(df))).iloc[-1]
    ema_score = 50
    if not any(pd.isna([ema7, ema25, ema99])):
        if ema7 > ema25 > ema99: ema_score = 100
        elif ema7 < ema25 < ema99: ema_score = 0

    adx_col = [c for c in df.columns if c.startswith("ADX_")]
    adx_score = 50
    if adx_col:
        v = df[adx_col[0]].iloc[-1]
        if not pd.isna(v):
            adx_score = 100 if v > 40 else (int(30 + (v-25)/15*70) if v >= 25 else 30)

    st_dir_col = [c for c in df.columns if "SUPERTd_" in c]
    st_score = 50
    if st_dir_col:
        d = df[st_dir_col[0]].iloc[-1]
        if not pd.isna(d): st_score = 100 if d > 0 else 0

    trend = int(ema_score*0.4 + adx_score*0.3 + st_score*0.3)

    # Momentum
    rsi_col = [c for c in df.columns if c.startswith("RSI_")]
    rsi_score = 50
    if rsi_col:
        v = df[rsi_col[0]].iloc[-1]
        if not pd.isna(v): rsi_score = int(max(0, min(100, (v-30)/40*100)))

    macdh_col = [c for c in df.columns if c.startswith("MACDh_")]
    macd_score = 50
    if macdh_col:
        h = df[macdh_col[0]]
        latest, prev = h.iloc[-1], h.iloc[-2] if len(h) > 1 else h.iloc[-1]
        if not pd.isna(latest):
            if latest > 0 and latest > prev: macd_score = 100
            elif latest > 0: macd_score = 70
            elif latest < 0 and latest < prev: macd_score = 0
            else: macd_score = 30

    momentum = int(rsi_score*0.5 + macd_score*0.5)

    # Volume
    obv_col = [c for c in df.columns if c.startswith("OBV")]
    volume_score = 50
    if obv_col and len(df) >= 10:
        obv_trend = df[obv_col[0]].iloc[-1] > df[obv_col[0]].iloc[-5]
        price_trend = df["close"].iloc[-1] > df["close"].iloc[-5]
        volume_score = 100 if obv_trend == price_trend else 20

    total = int(trend*0.35 + momentum*0.30 + volume_score*0.20 + 50*0.15)
    return {"score": total, "label": label(total), "trend": trend, "momentum": momentum, "volume": volume_score}


def main():
    parser = argparse.ArgumentParser()
    for tf in ["15m", "1h", "4h", "1d"]:
        parser.add_argument(f"--klines_{tf.replace('m','m')}", required=False)
    args = parser.parse_args()

    results = {}
    weighted_total = 0.0
    total_weight = 0.0

    for tf, weight in WEIGHTS.items():
        klines_arg = getattr(args, f"klines_{tf}", None)
        if klines_arg:
            df = pd.DataFrame(json.loads(klines_arg))
            df.columns = [c.lower() for c in df.columns]
            for col in ["open","high","low","close","volume"]:
                if col in df.columns: df[col] = df[col].astype(float)
            s = score_single(df)
            results[tf] = s
            weighted_total += s["score"] * weight
            total_weight += weight

    final = int(weighted_total / total_weight) if total_weight > 0 else 50

    def label(s):
        if s >= 80: return "STRONG_BULLISH"
        elif s >= 60: return "BULLISH"
        elif s >= 40: return "NEUTRAL"
        elif s >= 20: return "BEARISH"
        return "STRONG_BEARISH"

    output = {
        "total": final,
        "label": label(final),
        "multiTimeframe": {tf: {"score": v["score"], "label": v["label"]} for tf, v in results.items()}
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
