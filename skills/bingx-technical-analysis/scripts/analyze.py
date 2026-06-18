import pandas as pd
import pandas_ta_classic as ta
from scipy.signal import argrelextrema
import json, sys, argparse
import numpy as np


def compute_score(df):
    score_parts = {}

    # Trend 35%
    ema7 = df.get("EMA_7", pd.Series([np.nan] * len(df))).iloc[-1]
    ema25 = df.get("EMA_25", pd.Series([np.nan] * len(df))).iloc[-1]
    ema99 = df.get("EMA_99", pd.Series([np.nan] * len(df))).iloc[-1]

    ema_score = 50
    if not any(pd.isna([ema7, ema25, ema99])):
        if ema7 > ema25 > ema99:
            ema_score = 100
        elif ema7 < ema25 < ema99:
            ema_score = 0

    adx_col = [c for c in df.columns if c.startswith("ADX_")]
    adx_score = 50
    if adx_col:
        adx_val = df[adx_col[0]].iloc[-1]
        if not pd.isna(adx_val):
            if adx_val > 40:
                adx_score = 100
            elif adx_val >= 25:
                adx_score = int(30 + (adx_val - 25) / 15 * 70)
            else:
                adx_score = 30

    st_col = [c for c in df.columns if "SUPERT_" in c and "d" not in c.lower()]
    st_score = 50
    if st_col:
        st_dir_col = [c for c in df.columns if "SUPERTd_" in c]
        if st_dir_col:
            st_dir = df[st_dir_col[0]].iloc[-1]
            if not pd.isna(st_dir):
                st_score = 100 if st_dir > 0 else 0

    trend_score = int(ema_score * 0.4 + adx_score * 0.3 + st_score * 0.3)

    # Momentum 30%
    rsi_col = [c for c in df.columns if c.startswith("RSI_")]
    rsi_score = 50
    if rsi_col:
        rsi_val = df[rsi_col[0]].iloc[-1]
        if not pd.isna(rsi_val):
            rsi_score = int(max(0, min(100, (rsi_val - 30) / 40 * 100)))

    macd_h_col = [c for c in df.columns if c.startswith("MACDh_")]
    macd_score = 50
    if macd_h_col:
        hist = df[macd_h_col[0]]
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else latest
        if not pd.isna(latest):
            if latest > 0 and latest > prev:
                macd_score = 100
            elif latest > 0:
                macd_score = 70
            elif latest < 0 and latest < prev:
                macd_score = 0
            else:
                macd_score = 30

    momentum_score = int(rsi_score * 0.5 + macd_score * 0.5)

    # Volume 20%
    obv_col = [c for c in df.columns if c.startswith("OBV")]
    volume_score = 50
    if obv_col:
        obv = df[obv_col[0]]
        close = df["close"]
        if len(obv) >= 10:
            obv_trend = obv.iloc[-1] > obv.iloc[-5]
            price_trend = close.iloc[-1] > close.iloc[-5]
            volume_score = 100 if obv_trend == price_trend else 20

    # Pattern 15%
    cdl_cols = [c for c in df.columns if c.startswith("CDL")]
    pattern_score = 50
    if cdl_cols:
        recent = df[cdl_cols].tail(5)
        bullish = (recent > 0).sum().sum()
        bearish = (recent < 0).sum().sum()
        if bullish > bearish:
            pattern_score = min(100, 50 + bullish * 10)
        elif bearish > bullish:
            pattern_score = max(0, 50 - bearish * 10)

    total = int(
        trend_score * 0.35
        + momentum_score * 0.30
        + volume_score * 0.20
        + pattern_score * 0.15
    )

    def label(s):
        if s >= 80:
            return "STRONG_BULLISH"
        elif s >= 60:
            return "BULLISH"
        elif s >= 40:
            return "NEUTRAL"
        elif s >= 20:
            return "BEARISH"
        return "STRONG_BEARISH"

    score_parts["trend"] = trend_score
    score_parts["momentum"] = momentum_score
    score_parts["volume"] = volume_score
    score_parts["pattern"] = pattern_score
    score_parts["total"] = total
    score_parts["label"] = label(total)
    return score_parts


def detect_divergence(df):
    results = []
    close = df["close"].values
    rsi_col = [c for c in df.columns if c.startswith("RSI_")]
    macd_col = [c for c in df.columns if c.startswith("MACD_")]
    obv_col = [c for c in df.columns if c.startswith("OBV")]

    def check_div(indicator_series, name):
        if indicator_series is None or len(indicator_series) < 20:
            return {"indicator": name, "type": "NONE"}
        ind = indicator_series.values
        price_lows = argrelextrema(close[-30:], np.less, order=3)[0]
        if len(price_lows) >= 2:
            p1, p2 = price_lows[-2], price_lows[-1]
            if close[-30:][p2] < close[-30:][p1] and ind[-30:][p2] > ind[-30:][p1]:
                return {"indicator": name, "type": "BULLISH_DIVERGENCE"}
            if close[-30:][p2] > close[-30:][p1] and ind[-30:][p2] < ind[-30:][p1]:
                return {"indicator": name, "type": "BEARISH_DIVERGENCE"}
        return {"indicator": name, "type": "NONE"}

    results.append(check_div(df[rsi_col[0]] if rsi_col else None, "RSI"))
    results.append(check_div(df[macd_col[0]] if macd_col else None, "MACD"))
    results.append(check_div(df[obv_col[0]] if obv_col else None, "OBV"))
    return results


def find_support_resistance(df, n_levels=2):
    close = df["close"].values
    high = df["high"].values
    low = df["low"].values

    resistance_idx = argrelextrema(high, np.greater, order=5)[0]
    support_idx = argrelextrema(low, np.less, order=5)[0]

    resistances = sorted(
        [{"price": round(float(high[i]), 2), "strength": 1} for i in resistance_idx[-5:]],
        key=lambda x: x["price"],
        reverse=True,
    )[:n_levels]

    supports = sorted(
        [{"price": round(float(low[i]), 2), "strength": 1} for i in support_idx[-5:]],
        key=lambda x: x["price"],
    )[:n_levels]

    return {"support": supports, "resistance": resistances}


def extract_latest(df, mode):
    result = {}
    last = df.iloc[-1]

    if mode in ("full", "indicator"):
        indicators = {}

        rsi_col = [c for c in df.columns if c.startswith("RSI_")]
        if rsi_col:
            v = last[rsi_col[0]]
            sig = "OVERBOUGHT" if v > 70 else ("OVERSOLD" if v < 30 else "NEUTRAL")
            indicators["rsi"] = {"value": round(float(v), 2), "signal": sig}

        macd_col = [c for c in df.columns if c.startswith("MACD_") and "h" not in c.lower() and "s" not in c.lower()]
        macdh_col = [c for c in df.columns if c.startswith("MACDh_")]
        macds_col = [c for c in df.columns if c.startswith("MACDs_")]
        if macd_col and macdh_col and macds_col:
            m = last[macd_col[0]]
            h = last[macdh_col[0]]
            s = last[macds_col[0]]
            sig = "BUY" if h > 0 else "SELL"
            indicators["macd"] = {
                "macd": round(float(m), 4),
                "signal_line": round(float(s), 4),
                "histogram": round(float(h), 4),
                "signal": sig,
            }

        ema_cols = {c: last[c] for c in df.columns if c.startswith("EMA_")}
        if ema_cols:
            vals = {c: round(float(v), 2) for c, v in ema_cols.items() if not pd.isna(v)}
            sorted_vals = sorted(vals.items(), key=lambda x: int(x[0].split("_")[1]))
            ema_entry = {k.lower(): v for k, v in sorted_vals}
            prices = [v for _, v in sorted_vals]
            sig = "BULLISH" if prices == sorted(prices, reverse=True) else ("BEARISH" if prices == sorted(prices) else "MIXED")
            ema_entry["signal"] = sig
            indicators["ema"] = ema_entry

        bb_upper = [c for c in df.columns if c.startswith("BBU_")]
        bb_mid = [c for c in df.columns if c.startswith("BBM_")]
        bb_lower = [c for c in df.columns if c.startswith("BBL_")]
        if bb_upper and bb_mid and bb_lower:
            u, m, l = last[bb_upper[0]], last[bb_mid[0]], last[bb_lower[0]]
            pctb = (last["close"] - l) / (u - l) if (u - l) != 0 else 0.5
            indicators["bbands"] = {
                "upper": round(float(u), 2),
                "middle": round(float(m), 2),
                "lower": round(float(l), 2),
                "pctb": round(float(pctb), 3),
            }

        adx_col = [c for c in df.columns if c.startswith("ADX_")]
        dmp_col = [c for c in df.columns if c.startswith("DMP_")]
        dmn_col = [c for c in df.columns if c.startswith("DMN_")]
        if adx_col:
            adx_val = last[adx_col[0]]
            dmp = last[dmp_col[0]] if dmp_col else None
            dmn = last[dmn_col[0]] if dmn_col else None
            sig = "BULLISH" if (dmp and dmn and dmp > dmn) else "BEARISH"
            indicators["adx"] = {
                "adx": round(float(adx_val), 2),
                "plus_di": round(float(dmp), 2) if dmp else None,
                "minus_di": round(float(dmn), 2) if dmn else None,
                "signal": sig,
            }

        st_col = [c for c in df.columns if "SUPERT_" in c and "d" not in c and "l" not in c]
        st_dir_col = [c for c in df.columns if "SUPERTd_" in c]
        if st_col and st_dir_col:
            st_val = last[st_col[0]]
            st_dir = last[st_dir_col[0]]
            sig = "BUY" if st_dir > 0 else "SELL"
            indicators["supertrend"] = {
                "value": round(float(st_val), 2),
                "direction": "UP" if st_dir > 0 else "DOWN",
                "signal": sig,
            }

        result["indicators"] = indicators

    if mode in ("full", "pattern"):
        cdl_cols = [c for c in df.columns if c.startswith("CDL")]
        patterns = []
        recent = df[cdl_cols].tail(5) if cdl_cols else pd.DataFrame()
        for i, row in recent.iterrows():
            bars_ago = len(recent) - 1 - list(recent.index).index(i)
            for col in cdl_cols:
                val = row[col]
                if not pd.isna(val) and val != 0:
                    ptype = "BULLISH" if val > 0 else "BEARISH"
                    patterns.append({
                        "name": col.lower(),
                        "type": ptype,
                        "barsAgo": bars_ago,
                    })
        result["patterns"] = patterns

    if mode in ("full", "score"):
        result["score"] = compute_score(df)

    if mode == "full":
        result["divergences"] = detect_divergence(df)
        result["supportResistance"] = find_support_resistance(df)

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="full")
    parser.add_argument("--symbol", default="BTC-USDT")
    parser.add_argument("--interval", default="4h")
    parser.add_argument("--klines", required=True)
    args = parser.parse_args()

    df = pd.DataFrame(json.loads(args.klines))
    df.columns = [c.lower() for c in df.columns]
    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = df[col].astype(float)
    if "time" in df.columns:
        df.index = pd.to_datetime(df["time"], unit="ms", utc=True)
        df.index.name = "date"

    if len(df) < 50:
        print(json.dumps({"error": "Insufficient kline data, at least 50 candles required"}))
        sys.exit(1)

    if args.mode in ("full", "indicator"):
        df.ta.strategy("All")

    if args.mode in ("full", "pattern"):
        df.ta.cdl_pattern(name="all")

    result = extract_latest(df, args.mode)
    result["symbol"] = args.symbol
    result["interval"] = args.interval
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
