import json, argparse, sys
import numpy as np

MAKER_FEE = 0.0002  # 0.02%
TAKER_FEE = 0.0005  # 0.05%

# Amount weight per level (max 5 levels)
LEVEL_WEIGHTS = {
    1: [1.0],
    2: [0.6, 0.4],
    3: [0.4, 0.3, 0.3],
    4: [0.4, 0.3, 0.2, 0.1],
    5: [0.4, 0.25, 0.15, 0.1, 0.1],
}


def parse_orderbook(ob: dict, direction: str):
    bids = ob.get("bids", [])  # [[price, qty], ...]
    asks = ob.get("asks", [])

    if not bids or not asks:
        return None, None, None

    best_bid = float(bids[0][0])
    best_ask = float(asks[0][0])
    spread = best_ask - best_bid

    base_price = best_bid if direction == "LONG" else best_ask
    return base_price, spread, best_ask if direction == "LONG" else best_bid


def calc_tick_size(price: float) -> float:
    if price >= 10000:
        return 0.1
    elif price >= 1000:
        return 0.01
    elif price >= 100:
        return 0.001
    elif price >= 1:
        return 0.0001
    return 0.00001


def plan_mode(args, ob: dict) -> dict:
    direction = args.direction.upper()
    amount = float(args.amount)
    levels = max(1, min(5, int(args.levels)))

    base_price, spread, market_price = parse_orderbook(ob, direction)
    if base_price is None:
        return {"error": "Invalid order book data, cannot calculate order plan"}

    tick = calc_tick_size(base_price)
    interval = max(spread * 0.5, tick)

    weights = LEVEL_WEIGHTS[levels]
    orders = []

    for i in range(levels):
        if direction == "LONG":
            price = round(base_price - interval * i, 8)
            price = round(round(price / tick) * tick, 8)
        else:
            price = round(base_price + interval * i, 8)
            price = round(round(price / tick) * tick, 8)

        amt = round(amount * weights[i], 4)
        orders.append({"level": i + 1, "price": price, "amount_usdt": amt})

    # Estimated avg price (assuming full fill)
    total_val = sum(o["amount_usdt"] for o in orders)
    estimated_avg = sum(o["price"] * o["amount_usdt"] for o in orders) / total_val if total_val > 0 else base_price

    # Estimated fee savings
    fee_saved_pct = TAKER_FEE - MAKER_FEE
    fee_saved = round(total_val * fee_saved_pct, 4)

    return {
        "orders": orders,
        "base_price": round(base_price, 8),
        "market_price": round(market_price, 8),
        "spread": round(spread, 8),
        "interval": round(interval, 8),
        "estimated_avg": round(estimated_avg, 4),
        "fee_saved_pct": fee_saved_pct,
        "fee_saved_usdt": fee_saved,
        "total_amount": round(total_val, 4),
    }


def adjust_mode(args, ob: dict) -> dict:
    direction = args.direction.upper()
    current_orders = json.loads(args.current_orders)

    base_price, spread, _ = parse_orderbook(ob, direction)
    if base_price is None:
        return {"error": "Invalid order book data"}

    to_cancel = []
    to_replace = []

    for order in current_orders:
        if order.get("status") == "FILLED":
            continue

        order_price = float(order["price"])
        deviation = abs(order_price - base_price) / base_price

        if deviation > 0.01:
            to_cancel.append(order["orderId"])
            to_replace.append(order)
        elif direction == "LONG" and order_price > base_price * 1.003:
            to_cancel.append(order["orderId"])
            to_replace.append(order)
        elif direction == "SHORT" and order_price < base_price * 0.997:
            to_cancel.append(order["orderId"])
            to_replace.append(order)

    return {
        "to_cancel": to_cancel,
        "to_replace": to_replace,
        "new_base_price": round(base_price, 8),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["plan", "adjust"])
    parser.add_argument("--symbol", default="BTC-USDT")
    parser.add_argument("--direction", required=True)
    parser.add_argument("--amount", default="1000")
    parser.add_argument("--levels", default="3")
    parser.add_argument("--orderbook", required=True)
    parser.add_argument("--current-orders", default="[]")
    args = parser.parse_args()

    ob = json.loads(args.orderbook)

    if args.mode == "plan":
        result = plan_mode(args, ob)
    else:
        result = adjust_mode(args, ob)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
