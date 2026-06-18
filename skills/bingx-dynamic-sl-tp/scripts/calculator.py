import json, argparse, sys
import pandas as pd
import pandas_ta_classic as ta
import numpy as np
from scipy.signal import argrelextrema


def load_df(klines_json: str) -> pd.DataFrame:
    df = pd.DataFrame(json.loads(klines_json))
    df.columns = [c.lower() for c in df.columns]
    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "time" in df.columns:
        df.index = pd.to_datetime(df["time"], unit="ms", utc=True)
        df.index.name = "date"
    return df.dropna(subset=["close"])


def calc_atr(df: pd.DataFrame, period: int = 14) -> float:
    df.ta.atr(length=period, append=True)
    col = f"ATRr_{period}"
    if col not in df.columns:
        col = next((c for c in df.columns if c.startswith("ATR")), None)
    return float(df[col].iloc[-1]) if col else float(df["high"].iloc[-1] - df["low"].iloc[-1])


def find_structure(df: pd.DataFrame, direction: str):
    lows = argrelextrema(df["low"].values, np.less, order=5)[0]
    highs = argrelextrema(df["high"].values, np.greater, order=5)[0]
    if direction == "long":
        levels = sorted([df["low"].iloc[i] for i in lows], reverse=True)
        return levels[0] if levels else float(df["low"].tail(20).min())
    else:
        levels = sorted([df["high"].iloc[i] for i in highs])
        return levels[0] if levels else float(df["high"].tail(20).max())


def calc_sl(direction: str, entry: float, strategy: str, atr: float,
            atr_mult: float, df: pd.DataFrame, fixed_pct: float = 0.02) -> dict:
    if strategy == "atr":
        dist = atr * atr_mult
        price = entry - dist if direction == "long" else entry + dist
        return {"price": round(price, 4), "strategy": f"ATR×{atr_mult}", "distance_pct": round(dist/entry*100, 3)}

    elif strategy == "volatility":
        df.ta.bbands(length=20, append=True)
        bb_u = next((c for c in df.columns if c.startswith("BBU_")), None)
        bb_l = next((c for c in df.columns if c.startswith("BBL_")), None)
        if bb_u and bb_l:
            width = float(df[bb_u].iloc[-1]) - float(df[bb_l].iloc[-1])
            dist = width * 0.4
        else:
            dist = atr * atr_mult
        price = entry - dist if direction == "long" else entry + dist
        return {"price": round(price, 4), "strategy": "Bollinger Band Volatility", "distance_pct": round(dist/entry*100, 3)}

    elif strategy == "structure":
        struct_level = find_structure(df, direction)
        if direction == "long":
            price = struct_level * 0.998
        else:
            price = struct_level * 1.002
        dist = abs(entry - price)
        return {"price": round(price, 4), "strategy": "Structure Stop", "distance_pct": round(dist/entry*100, 3)}

    else:  # fixed_pct
        dist = entry * fixed_pct
        price = entry - dist if direction == "long" else entry + dist
        return {"price": round(price, 4), "strategy": f"Fixed {fixed_pct*100}%", "distance_pct": round(fixed_pct*100, 3)}


def calc_tp(direction: str, entry: float, sl_price: float,
            tp_mode: str, rr: float, atr: float) -> tuple:
    R = abs(entry - sl_price)

    if tp_mode == "ratio":
        price = entry + R * rr if direction == "long" else entry - R * rr
        tps = [{"level": 1, "price": round(price, 4), "close_pct": 100, "type": "limit"}]
        trailing = None

    elif tp_mode == "levels":
        splits = [40, 30, 30]
        ratios = [1.0, 2.0, 3.0]
        tps = []
        for i, (r, s) in enumerate(zip(ratios, splits)):
            p = entry + R * r if direction == "long" else entry - R * r
            tps.append({"level": i+1, "price": round(p, 4), "close_pct": s, "type": "limit"})
        trailing = None

    elif tp_mode == "trailing":
        cb = round(atr / entry * 100, 3)
        activation = entry + R if direction == "long" else entry - R
        tps = []
        trailing = {"callback_rate": cb, "activation_price": round(activation, 4)}

    elif tp_mode == "breakeven":
        tp1 = entry + R if direction == "long" else entry - R
        tp2 = entry + R * 2 if direction == "long" else entry - R * 2
        tps = [
            {"level": 1, "price": round(tp1, 4), "close_pct": 50, "type": "limit", "breakeven_trigger": True},
            {"level": 2, "price": round(tp2, 4), "close_pct": 50, "type": "limit"},
        ]
        trailing = None

    else:  # hybrid
        tp1 = entry + R if direction == "long" else entry - R
        tp2 = entry + R * 2 if direction == "long" else entry - R * 2
        cb = round(atr / entry * 100, 3)
        tps = [
            {"level": 1, "price": round(tp1, 4), "close_pct": 40, "type": "limit"},
            {"level": 2, "price": round(tp2, 4), "close_pct": 30, "type": "limit"},
            {"level": 3, "price": None, "close_pct": 30, "type": "trailing"},
        ]
        trailing = {"callback_rate": cb, "activation_price": round(tp2, 4)}

    return tps, trailing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--direction", required=True, choices=["long", "short"])
    parser.add_argument("--entry-price", type=float, required=True)
    parser.add_argument("--strategy", default="atr", choices=["atr", "volatility", "structure", "fixed_pct"])
    parser.add_argument("--atr-multiplier", type=float, default=1.5)
    parser.add_argument("--tp-mode", default="levels", choices=["ratio", "levels", "trailing", "breakeven", "hybrid"])
    parser.add_argument("--risk-reward", type=float, default=2.0)
    parser.add_argument("--fixed-pct", type=float, default=0.02)
    parser.add_argument("--klines", required=True)
    parser.add_argument("--position-size", type=float, default=0)
    args = parser.parse_args()

    df = load_df(args.klines)
    if len(df) < 20:
        print(json.dumps({"error": "Insufficient kline data, at least 20 candles required"}))
        sys.exit(1)

    atr = calc_atr(df)
    sl = calc_sl(args.direction, args.entry_price, args.strategy,
                 atr, args.atr_multiplier, df, args.fixed_pct)
    tps, trailing = calc_tp(args.direction, args.entry_price, sl["price"],
                            args.tp_mode, args.risk_reward, atr)

    R = abs(args.entry_price - sl["price"])
    actual_rr = abs(tps[-1]["price"] - args.entry_price) / R if tps and tps[-1]["price"] else args.risk_reward

    result = {
        "direction": args.direction,
        "entry_price": args.entry_price,
        "stop_loss": sl,
        "take_profit": tps,
        "trailing": trailing,
        "atr": round(atr, 4),
        "risk_reward": round(actual_rr, 2),
    }

    if args.position_size > 0:
        risk_amount = R * args.position_size
        result["risk_amount"] = round(risk_amount, 4)
        if tps and tps[-1]["price"]:
            reward_amount = abs(tps[-1]["price"] - args.entry_price) * args.position_size
            result["reward_amount"] = round(reward_amount, 4)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
