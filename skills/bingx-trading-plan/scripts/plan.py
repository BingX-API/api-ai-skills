import json, argparse, sys
import numpy as np


TIERS = {
    "conservative": {
        "risk_pct":    1.0,
        "atr_mult":    2.0,
        "rrr":         [3.0],
        "tp_splits":   [1.0],
        "leverage":    "<= 3x",
        "entry_mode":  "Limit order near support or resistance",
        "position_pct":"1% account",
    },
    "steady": {
        "risk_pct":    2.0,
        "atr_mult":    1.5,
        "rrr":         [2.0, 3.0],
        "tp_splits":   [0.5, 0.5],
        "leverage":    "3x - 10x",
        "entry_mode":  "Limit or market order",
        "position_pct":"2% account",
    },
    "aggressive": {
        "risk_pct":    4.0,
        "atr_mult":    1.0,
        "rrr":         [1.5, 2.0, 3.0],
        "tp_splits":   [0.3, 0.3, 0.4],
        "leverage":    "10x - 20x",
        "entry_mode":  "Market momentum entry",
        "position_pct":"3-5% account",
        "trailing_stop": True,
    },
}


def calc_atr(sr: dict, price: float) -> float:
    supports = sr.get("support", [])
    resistances = sr.get("resistance", [])
    if supports and resistances:
        nearest_sup = max([s["price"] for s in supports], default=price * 0.97)
        nearest_res = min([r["price"] for r in resistances], default=price * 1.03)
        return (nearest_res - nearest_sup) / 4
    return price * 0.015  # fallback ATR-style distance


def snap_to_sr(price: float, sr_levels: list, direction: str, tolerance: float = 0.003) -> float:
    for level in sr_levels:
        lp = level["price"]
        if abs(lp - price) / price < tolerance:
            if direction == "LONG":
                return min(price, lp)
            else:
                return max(price, lp)
    return price


def build_plan(tier_name: str, tier: dict, direction: str, price: float, atr: float, sr: dict) -> dict:
    supports = sorted([s["price"] for s in sr.get("support", [])], reverse=True)
    resistances = sorted([r["price"] for r in sr.get("resistance", [])], reverse=False)

    if direction == "LONG":
        entry_low = supports[0] if supports else round(price * 0.995, 2)
        entry_high = round(price, 2)
        raw_sl = price - atr * tier["atr_mult"]
        stop_loss = snap_to_sr(raw_sl, sr.get("support", []), "LONG")
        stop_loss = round(stop_loss, 2)
        risk = price - stop_loss
        take_profits = [
            {"price": round(price + risk * r, 2), "ratio": f"R:{r}", "split": f"{int(s*100)}%"}
            for r, s in zip(tier["rrr"], tier["tp_splits"])
        ]
    else:
        entry_high = resistances[0] if resistances else round(price * 1.005, 2)
        entry_low = round(price, 2)
        raw_sl = price + atr * tier["atr_mult"]
        stop_loss = snap_to_sr(raw_sl, sr.get("resistance", []), "SHORT")
        stop_loss = round(stop_loss, 2)
        risk = stop_loss - price
        take_profits = [
            {"price": round(price - risk * r, 2), "ratio": f"R:{r}", "split": f"{int(s*100)}%"}
            for r, s in zip(tier["rrr"], tier["tp_splits"])
        ]

    rrr_str = f"{tier['rrr'][-1]:.1f}:1"

    plan = {
        "tier": tier_name,
        "entry_mode": tier["entry_mode"],
        "entry_zone": [round(min(entry_low, entry_high), 2), round(max(entry_low, entry_high), 2)],
        "stop_loss": stop_loss,
        "take_profit": take_profits,
        "risk_reward": rrr_str,
        "leverage": tier["leverage"],
        "position_pct": tier["position_pct"],
    }
    if tier.get("trailing_stop"):
        plan["trailing_stop"] = True
    return plan


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTC-USDT")
    parser.add_argument("--direction", default="auto")
    parser.add_argument("--risk-tier", default="all")
    parser.add_argument("--score-result", required=True)
    parser.add_argument("--current-price", type=float, required=True)
    parser.add_argument("--support-resistance", required=True)
    args = parser.parse_args()

    score_data = json.loads(args.score_result)
    sr = json.loads(args.support_resistance)
    price = args.current_price
    composite = score_data["composite_score"]

    # Direction decision
    if args.direction in ("long", "short"):
        direction = args.direction.upper()
        contrarian = (direction == "LONG" and composite < -29) or (direction == "SHORT" and composite > 29)
    else:
        direction = score_data["direction"]
        contrarian = False

    if direction == "NEUTRAL":
        direction = "LONG"  # neutral mode calculates long first, then adds short reference

    atr = calc_atr(sr, price)

    # Tier selection
    tier_names = ["conservative", "steady", "aggressive"] if args.risk_tier == "all" else [args.risk_tier]
    plans = [build_plan(name, TIERS[name], direction, price, atr, sr) for name in tier_names]

    result = {
        "symbol": args.symbol,
        "direction": direction,
        "score": composite,
        "label": score_data["label"],
        "confidence": score_data["confidence"],
        "contrarian_warning": contrarian,
        "plans": plans,
    }

    if score_data["direction"] == "NEUTRAL":
        result["neutral_warning"] = True
        # Add the opposite reference plan.
        opp = "SHORT" if direction == "LONG" else "LONG"
        opp_plans = [build_plan(name, TIERS[name], opp, price, atr, sr) for name in tier_names]
        result["opposite_plans"] = opp_plans

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
