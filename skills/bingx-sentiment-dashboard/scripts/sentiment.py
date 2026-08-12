"""4-dimension sentiment aggregation engine"""
import json, argparse, sys
import numpy as np
import pandas as pd


WEIGHTS = {"fear_greed": 0.30, "funding": 0.25, "oi": 0.25, "ahr999": 0.20}


def score_fear_greed(fg) -> tuple:
    # Accepts a single dict, an upstream history object, or Lindorm rows with
    # extraData as a JSON string.
    if not fg:
        return None, "Fear & Greed Index unavailable"
    if isinstance(fg, dict) and "data" in fg and isinstance(fg["data"], list):
        entry = fg["data"][0] if fg["data"] else {}
        if isinstance(entry, dict) and "extraData" in entry:
            entry = json.loads(entry.get("extraData") or "{}")
    elif isinstance(fg, list):
        entry = fg[0] if fg else {}
        if isinstance(entry, dict) and "extraData" in entry:
            entry = json.loads(entry.get("extraData") or "{}")
    else:
        entry = fg
    if not entry:
        return None, "Fear & Greed Index unavailable"

    if "values" in entry:
        values = entry.get("values") or []
        val = int(float(values[-1])) if values else 50
    else:
        val = int(float(entry.get("value", 50)))

    classification = entry.get("value_classification") or classify_fear_greed(val)
    # linear map 0-100 to -100..+100
    score = int((val - 50) * 2)
    return score, f"Fear & Greed = {val} ({classification})"


def classify_fear_greed(value: int) -> str:
    if value <= 24:
        return "Extreme Fear"
    if value <= 44:
        return "Fear"
    if value <= 55:
        return "Neutral"
    if value <= 75:
        return "Greed"
    return "Extreme Greed"


def score_funding(funding: list) -> tuple:
    if not funding:
        return 0, "No funding rate data"
    rates = [float(f.get("lastFundingRate") or f.get("fundingRate") or 0) for f in funding]
    rates = [r for r in rates if r != 0]
    if not rates:
        return 0, "No valid funding rate data"
    avg = np.mean(rates)
    pos_pct = sum(1 for r in rates if r > 0) / len(rates) * 100

    score = int(np.clip(avg / 0.001 * 30, -100, 100))
    if pos_pct > 60:
        score = min(score + 20, 100)
    elif pos_pct < 40:
        score = max(score - 20, -100)

    return score, f"Market average {avg*100:.4f}%, {pos_pct:.0f}% positive funding"


def score_oi(oi_data: list, tickers: list) -> tuple:
    if not oi_data:
        return 0, "No OI data"
    ticker_map = {t.get("symbol"): t for t in tickers} if tickers else {}
    changes = []
    for item in oi_data:
        sym = item.get("symbol", "")
        oi_cur = float(item.get("openInterest") or 0)
        oi_prev = float(item.get("openInterestPrev") or oi_cur)
        if oi_prev == 0:
            continue
        oi_chg = (oi_cur - oi_prev) / oi_prev
        price_chg = float(ticker_map.get(sym, {}).get("priceChangePercent") or 0) / 100
        # OI up + price up = long buildup (bullish); OI up + price down = short buildup (bearish)
        if oi_chg > 0:
            changes.append(oi_chg * (1 if price_chg >= 0 else -1))
        else:
            changes.append(oi_chg)

    if not changes:
        return 0, "No valid OI change data"
    avg_chg = np.mean(changes)
    score = int(np.clip(avg_chg * 200, -100, 100))
    total_chg_pct = avg_chg * 100
    return score, f"Market average OI change {total_chg_pct:+.2f}%"


def score_ahr999(ahr_result: dict) -> tuple:
    if not ahr_result or "error" in ahr_result:
        return None, "AHR999 calculation failed"
    score = ahr_result.get("score", 0)
    val = ahr_result.get("ahr999", 0)
    zone = ahr_result.get("zone", "")
    return score, f"{val} ({zone})"


def label(score: int) -> str:
    if score >= 70: return "EXTREME_GREED"
    elif score >= 30: return "GREED"
    elif score >= -29: return "NEUTRAL"
    elif score >= -69: return "FEAR"
    return "EXTREME_FEAR"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="full")
    parser.add_argument("--fear-greed", default="{}")
    parser.add_argument("--funding", default="[]")
    parser.add_argument("--oi", default="[]")
    parser.add_argument("--tickers", default="[]")
    parser.add_argument("--ahr999-result", default="{}")
    args = parser.parse_args()

    fg = json.loads(args.fear_greed)
    funding = json.loads(args.funding)
    oi = json.loads(args.oi)
    tickers = json.loads(args.tickers)
    ahr_result = json.loads(args.ahr999_result)

    fg_score, fg_detail = score_fear_greed(fg if fg else None)
    fr_score, fr_detail = score_funding(funding)
    oi_score, oi_detail = score_oi(oi, tickers)
    ahr_score, ahr_detail = score_ahr999(ahr_result if ahr_result else None)

    # weighted composite from available dimensions
    total_weight = 0.0
    composite = 0.0
    dimensions = {}

    for dim, w, sc, detail in [
        ("fear_greed", WEIGHTS["fear_greed"], fg_score, fg_detail),
        ("funding",    WEIGHTS["funding"],    fr_score, fr_detail),
        ("oi",         WEIGHTS["oi"],         oi_score, oi_detail),
        ("ahr999",     WEIGHTS["ahr999"],     ahr_score, ahr_detail),
    ]:
        if sc is not None:
            composite += sc * w
            total_weight += w
        dimensions[dim] = {"score": sc, "detail": detail}

    if total_weight > 0:
        composite = int(composite / total_weight)
    else:
        composite = 0

    composite = max(-100, min(100, composite))

    # top 5 funding rates by absolute value
    top5 = []
    if funding:
        sorted_f = sorted(funding, key=lambda x: abs(float(x.get("lastFundingRate") or 0)), reverse=True)[:5]
        top5 = [{"symbol": f["symbol"], "rate": float(f.get("lastFundingRate") or 0)} for f in sorted_f]

    result = {
        "composite_score": composite,
        "label": label(composite),
        "dimensions": dimensions,
        "top5_funding": top5,
        "available_dimensions": [d for d, v in dimensions.items() if v["score"] is not None],
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
