"""
AHR999 index calculation
Formula: AHR999 = (current_price / 200d_dca_cost) * (current_price / exp_growth_value)
exp_growth_value = 10^(5.84 * log10(days_since_genesis) - 17.01)
BTC genesis date: 2009-01-03
"""
import json, argparse, sys
import numpy as np
import pandas as pd
from datetime import UTC, datetime

BTC_GENESIS = datetime(2009, 1, 3)

ZONES = [
    (float("-inf"), 0.45,  "Accumulation Zone", -75),
    (0.45,          1.2,   "DCA Zone",          -15),
    (1.2,           5.0,   "Wait Zone",          40),
    (5.0,           float("inf"), "Overheated Zone", 80),
]


def exp_growth_value(days_since_genesis: int) -> float:
    return 10 ** (5.84 * np.log10(days_since_genesis) - 17.01)


def zone_info(ahr: float):
    for lo, hi, name, score in ZONES:
        if lo <= ahr < hi:
            if lo == float("-inf"):
                zone_range = f"<{hi}"
            elif hi == float("inf"):
                zone_range = f">{lo}"
            else:
                zone_range = f"{lo}-{hi}"
            return name, zone_range, score
    return "Overheated Zone", ">5.0", 80


def normalize_klines(klines):
    if isinstance(klines, dict) and "data" in klines:
        klines = klines.get("data") or []
    if not klines:
        return pd.DataFrame()

    first = klines[0]
    if isinstance(first, dict):
        df = pd.DataFrame(klines)
        df.columns = [c.lower() for c in df.columns]
        return df

    columns = ["open_time", "open", "high", "low", "close", "volume", "close_time"]
    rows = []
    for row in klines:
        if isinstance(row, list) and len(row) >= 5:
            padded = row[:7] + [None] * max(0, 7 - len(row[:7]))
            rows.append(dict(zip(columns, padded)))
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--btc-kline", required=True)
    args = parser.parse_args()

    klines = json.loads(args.btc_kline)
    if not klines:
        print(json.dumps({"error": "BTC kline data is empty"}))
        sys.exit(1)

    df = normalize_klines(klines)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close"])

    if len(df) < 10:
        print(json.dumps({"error": "Insufficient kline data, at least 10 days required"}))
        sys.exit(1)

    current_price = float(df["close"].iloc[-1])
    dca_days = min(200, len(df))
    dca_cost = float(df["close"].tail(dca_days).mean())

    # days since BTC genesis
    now = datetime.now(UTC).replace(tzinfo=None)
    days_since_genesis = (now - BTC_GENESIS).days
    exp_val = exp_growth_value(days_since_genesis)

    ahr999 = (current_price / dca_cost) * (current_price / exp_val)
    zone_name, zone_range, score = zone_info(ahr999)

    result = {
        "ahr999": round(ahr999, 4),
        "zone": zone_name,
        "zone_range": zone_range,
        "current_price": round(current_price, 2),
        "dca_200d_cost": round(dca_cost, 2),
        "dca_days_used": dca_days,
        "exp_growth_value": round(exp_val, 2),
        "days_since_genesis": days_since_genesis,
        "score": score,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
