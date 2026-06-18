import pandas as pd
import pandas_ta_classic as ta
import json, argparse, sys


def ta_checks(ta_result: dict, price: float) -> dict:
    """Extract multi-dimension confirmation items from bingx-technical-analysis result."""
    if not ta_result:
        return {}

    indicators = ta_result.get("indicators", {})
    divergences = ta_result.get("divergences", [])
    sr = ta_result.get("supportResistance", {})
    patterns = ta_result.get("patterns", [])

    macd_signal = indicators.get("macd", {}).get("signal", "")
    st_signal = indicators.get("supertrend", {}).get("signal", "")

    div_map = {d["indicator"]: d["type"] for d in divergences}
    rsi_div = div_map.get("RSI", "NONE")
    obv_div = div_map.get("OBV", "NONE")

    # Near support level (within 5%)
    near_support = any(
        abs(price - s["price"]) / price < 0.05
        for s in sr.get("support", [])
    )

    # Bullish patterns in last 2 candles
    bullish_patterns = [p["name"] for p in patterns if p["type"] == "BULLISH" and p["barsAgo"] <= 2]

    return {
        "macd_bullish":      macd_signal == "BUY",
        "supertrend_up":     st_signal == "BUY",
        "no_rsi_divergence": rsi_div != "BEARISH_DIVERGENCE",
        "no_obv_divergence": obv_div != "BEARISH_DIVERGENCE",
        "near_support":      near_support,
        "bullish_patterns":  bullish_patterns,
        "ta_score":          ta_result.get("score", {}).get("total", 0),
        "ta_label":          ta_result.get("score", {}).get("label", ""),
    }


def build_confirmation(consecutive_oversold: bool, price_recovering: bool, ta: dict) -> tuple:
    """
    Combined confirmation logic:
    - Base conditions: consecutive oversold + reversal candle
    - Additional conditions: no bearish divergence + at least one of MACD/Supertrend bullish
    Returns (confirmation: bool, strength: str, details: dict)
    """
    checks = {
        "consecutive_oversold": consecutive_oversold,
        "price_recovering":     price_recovering,
        "no_rsi_divergence":    ta.get("no_rsi_divergence", True),
        "no_obv_divergence":    ta.get("no_obv_divergence", True),
        "momentum_bullish":     ta.get("macd_bullish", False) or ta.get("supertrend_up", False),
    }

    passed = sum(1 for v in checks.values() if v)

    if passed == 5:
        strength = "CONFIRMED"
        confirmed = True
    elif passed >= 3:
        strength = "WEAK"
        confirmed = False
    else:
        strength = "REJECTED"
        confirmed = False

    return confirmed, strength, checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["scan", "once", "monitor"])
    parser.add_argument("--symbol", default="BTC-USDT")
    parser.add_argument("--interval", default="1h")
    parser.add_argument("--rsi-period", type=int, default=14)
    parser.add_argument("--rsi-buy", type=float, default=30.0)
    parser.add_argument("--rsi-sell", type=float, default=70.0)
    parser.add_argument("--stop-loss-pct", type=float, default=3.0)
    parser.add_argument("--take-profit-pct", type=float, default=5.0)
    parser.add_argument("--klines", required=True)
    parser.add_argument("--ta-result", default="{}")  # output from bingx-technical-analysis
    args = parser.parse_args()

    df = pd.DataFrame(json.loads(args.klines))
    df.columns = [c.lower() for c in df.columns]
    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = df[col].astype(float)
    if "time" in df.columns:
        df.index = pd.to_datetime(df["time"], unit="ms", utc=True)
        df.index.name = "date"

    if len(df) < args.rsi_period + 5:
        print(json.dumps({"error": f"Insufficient kline data, at least {args.rsi_period + 5} candles required"}))
        sys.exit(1)

    rsi_col = f"RSI_{args.rsi_period}"
    df.ta.rsi(length=args.rsi_period, append=True)

    if rsi_col not in df.columns:
        print(json.dumps({"error": "RSI calculation failed"}))
        sys.exit(1)

    rsi_current = float(df[rsi_col].iloc[-1])
    rsi_prev = float(df[rsi_col].iloc[-2])
    price = float(df["close"].iloc[-1])
    open_price = float(df["open"].iloc[-1])

    # RSI signal evaluation
    if rsi_current < args.rsi_buy:
        signal = "OVERSOLD_BUY"
    elif rsi_current > args.rsi_sell:
        signal = "OVERBOUGHT_EXIT"
    else:
        signal = "NEUTRAL"

    consecutive_oversold = rsi_current < args.rsi_buy and rsi_prev < args.rsi_buy
    price_recovering = price > open_price

    # Multi-dimension TA confirmation
    ta_result = json.loads(args.ta_result)
    ta = ta_checks(ta_result, price)
    confirmation, strength, check_details = build_confirmation(consecutive_oversold, price_recovering, ta)

    result = {
        "signal": signal,
        "rsi_current": round(rsi_current, 2),
        "rsi_prev": round(rsi_prev, 2),
        "price": round(price, 4),
        "confirmation": confirmation,
        "confirmation_strength": strength,
        "checks": check_details,
        "consecutive_oversold": consecutive_oversold,
        "price_recovering": price_recovering,
        "ta_score": ta.get("ta_score", 0),
        "ta_label": ta.get("ta_label", ""),
        "macd_bullish": ta.get("macd_bullish"),
        "supertrend_up": ta.get("supertrend_up"),
        "no_rsi_divergence": ta.get("no_rsi_divergence"),
        "no_obv_divergence": ta.get("no_obv_divergence"),
        "near_support": ta.get("near_support"),
        "bullish_patterns": ta.get("bullish_patterns", []),
    }

    if args.mode != "scan":
        result["stop_loss"] = round(price * (1 - args.stop_loss_pct / 100), 4)
        result["take_profit"] = round(price * (1 + args.take_profit_pct / 100), 4)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
