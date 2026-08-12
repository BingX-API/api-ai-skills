import json, argparse, sys
import numpy as np


def first_number(data: dict, keys: list[str], default: float = 0.0) -> float:
    for key in keys:
        if key in data and data[key] is not None:
            return float(data[key])
    return default


def parse_row_extra(row: dict) -> dict:
    try:
        extra = json.loads(row.get("extraData") or "{}")
    except (TypeError, json.JSONDecodeError):
        extra = {}
    if isinstance(extra, dict):
        merged = dict(extra)
    else:
        merged = {}
    for key in ("indicatorType", "intervalVal", "exchange", "symbol", "ts", "dateString", "dataSource"):
        if key in row and key not in merged:
            merged[key] = row[key]
    return merged


def extract_lindorm_rows(payload) -> list[dict]:
    if isinstance(payload, list):
        rows = []
        for item in payload:
            rows.extend(extract_lindorm_rows(item))
        return rows

    if not isinstance(payload, dict):
        return []

    if isinstance(payload.get("data"), list):
        rows = []
        for row in payload.get("data") or []:
            if isinstance(row, dict):
                rows.append(parse_row_extra(row) if "extraData" in row else row)
        return rows

    nested = []
    for value in payload.values():
        if isinstance(value, (dict, list)):
            nested.extend(extract_lindorm_rows(value))
    if nested:
        return nested
    return [payload]


def parse_lindorm_rows(payload) -> dict:
    merged = {}
    for row in extract_lindorm_rows(payload):
        if isinstance(row, dict):
            merged.update(row)
    return merged


def score_trend(ta: dict) -> int:
    score = ta.get("score", {})
    trend = score.get("trend", 50)
    return int((trend - 50) * 2)  # 0-100 to -100..+100


def score_momentum(ta: dict) -> int:
    score = ta.get("score", {})
    momentum = score.get("momentum", 50)
    return int((momentum - 50) * 2)


def score_volume(ta: dict) -> int:
    score = ta.get("score", {})
    volume = score.get("volume", 50)
    return int((volume - 50) * 2)


def score_funding(market: dict) -> int:
    rate = float(market.get("fundingRate", 0))
    # Positive funding means longs pay shorts and can be a contrarian bearish signal.
    if rate > 0.001:
        return -min(100, int(rate / 0.003 * 100))
    elif rate < -0.001:
        return min(100, int(abs(rate) / 0.003 * 100))
    return 0


def score_sentiment(sentiment: dict) -> int:
    if not sentiment:
        return 0
    sentiment = parse_lindorm_rows(sentiment)
    ratio_weights = [
        ("global_account_long_short_ratio", 0.30),
        ("top_account_long_short_ratio", 0.30),
        ("top_position_long_short_ratio", 0.40),
        ("longShortRatio", 0.20),
    ]
    ratios = []
    for key, weight in ratio_weights:
        if key in sentiment and sentiment[key] is not None:
            ratios.append((float(sentiment[key]), weight))
    long_ratio = sum(value * weight for value, weight in ratios) / sum(weight for _, weight in ratios) if ratios else 1.0
    # Long-short ratio above 1.5 can mean crowded longs; below 0.7 can mean crowded shorts.
    if long_ratio > 1.5:
        return -min(100, int((long_ratio - 1.0) / 1.0 * 60))
    elif long_ratio < 0.7:
        return min(100, int((1.0 - long_ratio) / 0.5 * 60))
    return 0


def score_liquidation(sentiment: dict, market: dict | None = None) -> int:
    if not sentiment:
        return 0
    rows = extract_lindorm_rows(sentiment)
    sentiment = parse_lindorm_rows(sentiment)

    # Dense liquidation above price is bullish pressure; dense liquidation below is bearish pressure.
    liq_above = float(sentiment.get("liqAbove", 0) or 0)
    liq_below = float(sentiment.get("liqBelow", 0) or 0)

    if liq_above == 0 and liq_below == 0:
        market = market or {}
        current_price = first_number(
            market,
            ["currentPrice", "price", "markPrice", "lastPrice", "close"],
            0.0,
        )
        if current_price == 0:
            closes = [
                (float(row.get("time") or row.get("ts") or 0), float(row.get("close")))
                for row in rows
                if isinstance(row, dict) and row.get("close") is not None
            ]
            if closes:
                current_price = max(closes, key=lambda item: item[0])[1]

        if current_price > 0:
            for row in rows:
                if not isinstance(row, dict):
                    continue
                price_level = row.get("price_level")
                intensity = row.get("intensity")
                if price_level is None or intensity is None:
                    continue
                price_level = float(price_level)
                intensity = max(0.0, float(intensity))
                if price_level >= current_price:
                    liq_above += intensity
                else:
                    liq_below += intensity

    total = liq_above + liq_below
    if total == 0:
        return 0
    ratio = (liq_above - liq_below) / total
    return int(ratio * 80)


def confidence(score: int) -> str:
    abs_score = abs(score)
    if abs_score >= 60:
        return "HIGH"
    elif abs_score >= 30:
        return "MEDIUM"
    return "LOW"


def label(score: int) -> str:
    if score >= 70:
        return "STRONG_LONG"
    elif score >= 30:
        return "LONG"
    elif score >= -29:
        return "NEUTRAL"
    elif score >= -69:
        return "SHORT"
    return "STRONG_SHORT"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTC-USDT")
    parser.add_argument("--ta-result", required=True)
    parser.add_argument("--market-data", required=True)
    parser.add_argument("--sentiment-data", default="{}")
    args = parser.parse_args()

    ta = json.loads(args.ta_result)
    market = json.loads(args.market_data)
    sentiment = json.loads(args.sentiment_data)

    weights = {
        "trend":      0.25,
        "momentum":   0.20,
        "volume":     0.15,
        "funding":    0.15,
        "sentiment":  0.15,
        "liquidation": 0.10,
    }

    dimensions = {
        "trend":       score_trend(ta),
        "momentum":    score_momentum(ta),
        "volume":      score_volume(ta),
        "funding":     score_funding(market),
        "sentiment":   score_sentiment(sentiment),
        "liquidation": score_liquidation(sentiment, market),
    }

    composite = int(sum(dimensions[k] * w for k, w in weights.items()))
    composite = max(-100, min(100, composite))

    direction = "LONG" if composite > 29 else ("SHORT" if composite < -29 else "NEUTRAL")

    result = {
        "composite_score": composite,
        "label": label(composite),
        "direction": direction,
        "confidence": confidence(composite),
        "dimensions": dimensions,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
