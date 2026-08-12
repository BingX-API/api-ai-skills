"""OI anomaly detection"""
import json, argparse, sys
import pandas as pd


ALERT_THRESHOLD = 0.15   # Trigger when OI changes by more than 15%.
PRICE_THRESHOLD = 0.03   # Use price changes above 3% for direction context.


def classify(oi_change: float, price_change: float) -> str:
    if oi_change > ALERT_THRESHOLD:
        if price_change > PRICE_THRESHOLD:
            return "LONG_BUILDUP"
        elif price_change < -PRICE_THRESHOLD:
            return "SHORT_BUILDUP"
        return "OI_SURGE"
    elif oi_change < -ALERT_THRESHOLD:
        if abs(price_change) > PRICE_THRESHOLD:
            return "LIQUIDATION"
        return "OI_DROP"
    return "NORMAL"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--oi", required=True)
    parser.add_argument("--tickers", default="[]")
    args = parser.parse_args()

    oi_data = json.loads(args.oi)
    tickers = {t.get("symbol"): t for t in json.loads(args.tickers)}

    alerts = []
    for item in oi_data:
        symbol = item.get("symbol", "")
        oi_current = float(item.get("openInterest") or item.get("oi") or 0)
        oi_prev = float(item.get("openInterestPrev") or item.get("oi_prev") or oi_current)

        if oi_prev == 0:
            continue

        oi_change = (oi_current - oi_prev) / oi_prev
        ticker = tickers.get(symbol, {})
        price_change = float(ticker.get("priceChangePercent") or 0) / 100

        alert_type = classify(oi_change, price_change)
        if alert_type != "NORMAL":
            alerts.append({
                "symbol": symbol,
                "oi_change_pct": round(oi_change * 100, 2),
                "price_change_pct": round(price_change * 100, 2),
                "alert_type": alert_type,
            })

    alerts.sort(key=lambda x: abs(x["oi_change_pct"]), reverse=True)
    print(json.dumps({"alerts": alerts, "total": len(alerts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
