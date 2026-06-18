"""
Candlestick pattern recognition module.
python3 patterns.py --klines '[...]' --lookback 5
"""
import pandas as pd
import pandas_ta_classic as ta
import json, argparse


CDL_EN = {
    "cdl_doji_10_0.1": "Doji",
    "cdl_inside": "Inside",
    "cdl_hammer": "Hammer",
    "cdl_shootingstar": "Shooting Star",
    "cdl_engulfing": "Engulfing",
    "cdl_morningstar": "Morning Star",
    "cdl_eveningstar": "Evening Star",
    "cdl_3blackcrows": "Three Black Crows",
    "cdl_3whitesoldiers": "Three White Soldiers",
    "cdl_harami": "Harami",
    "cdl_haramicross": "Harami Cross",
    "cdl_spinningtop": "Spinning Top",
    "cdl_marubozu": "Marubozu",
    "cdl_dragonflydoji": "Dragonfly Doji",
    "cdl_gravestonedoji": "Gravestone Doji",
    "cdl_longlegdoji": "Long Legged Doji",
    "cdl_rickshawman": "Rickshaw Man",
    "cdl_highwave": "High Wave",
    "cdl_hangingman": "Hanging Man",
    "cdl_invertedhammer": "Inverted Hammer",
    "cdl_piercingline": "Piercing Line",
    "cdl_darkcloudcover": "Dark Cloud Cover",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--klines", required=True)
    parser.add_argument("--lookback", type=int, default=5)
    args = parser.parse_args()

    df = pd.DataFrame(json.loads(args.klines))
    df.columns = [c.lower() for c in df.columns]
    for col in ["open","high","low","close","volume"]:
        if col in df.columns: df[col] = df[col].astype(float)

    df.ta.cdl_pattern(name="all")
    cdl_cols = [c for c in df.columns if c.startswith("CDL")]

    patterns = []
    recent = df[cdl_cols].tail(args.lookback)
    idx_list = list(recent.index)

    for i, row in recent.iterrows():
        bars_ago = len(recent) - 1 - idx_list.index(i)
        for col in cdl_cols:
            val = row[col]
            if not __import__("math").isnan(val) and val != 0:
                name_en = CDL_EN.get(col.lower(), col)
                patterns.append({
                    "name": col.lower(),
                    "nameEn": name_en,
                    "type": "BULLISH" if val > 0 else "BEARISH",
                    "barsAgo": bars_ago,
                })

    bullish = sum(1 for p in patterns if p["type"] == "BULLISH")
    bearish = sum(1 for p in patterns if p["type"] == "BEARISH")

    print(json.dumps({
        "patterns": patterns,
        "summary": {"bullish": bullish, "bearish": bearish, "total": len(patterns)}
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
