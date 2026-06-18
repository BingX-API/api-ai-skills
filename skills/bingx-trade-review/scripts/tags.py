"""Tag system CRUD, operates on ~/.bingx-skills/trade-review/trades.json"""
import json, argparse, sys
from datetime import datetime
import storage

PRESET_TAGS = {
    "Entry Logic": ["Breakout Chase", "Pullback Long", "Oversold Bottom", "Trend Following", "Counter-Trend"],
    "Emotional State": ["Calm Execution", "Impulsive Trade", "Revenge Trade", "FOMO"],
    "Execution Quality": ["Strict Stop-Loss", "Trailing Stop", "Early Exit", "Held to Liquidation"],
    "Time Horizon": ["Intraday", "Swing", "Medium-Long Term"],
}


def cmd_add(trade_id, tag):
    data = storage.load()
    if trade_id not in data:
        data[trade_id] = {"trade_id": trade_id, "tags": [], "reflection": "", "created_at": ""}
    if tag not in data[trade_id]["tags"]:
        data[trade_id]["tags"].append(tag)
    storage.save(data)
    return {"ok": True, "trade_id": trade_id, "tags": data[trade_id]["tags"]}


def cmd_remove(trade_id, tag):
    data = storage.load()
    if trade_id in data and tag in data[trade_id].get("tags", []):
        data[trade_id]["tags"].remove(tag)
        storage.save(data)
    return {"ok": True, "trade_id": trade_id, "tags": data.get(trade_id, {}).get("tags", [])}


def cmd_list():
    return {"preset": PRESET_TAGS, "custom": _get_custom_tags()}


def _get_custom_tags():
    data = storage.load()
    all_tags = set()
    preset_flat = {t for cats in PRESET_TAGS.values() for t in cats}
    for v in data.values():
        for tag in v.get("tags", []):
            if tag not in preset_flat:
                all_tags.add(tag)
    return list(all_tags)


def cmd_stats(tag, trades_json):
    trades = json.loads(trades_json)
    tagged = [t for t in trades if tag in t.get("tags", [])]
    if not tagged:
        return {"error": f"No trades found with tag '{tag}'"}

    pnls = [float(t.get("realizedPnl") or t.get("pnl") or 0) for t in tagged]
    wins = sum(1 for p in pnls if p > 0)
    total = len(pnls)
    return {
        "tag": tag,
        "count": total,
        "wins": wins,
        "losses": total - wins,
        "win_rate": round(wins / total * 100, 1) if total > 0 else 0,
        "total_pnl": round(sum(pnls), 4),
        "avg_pnl": round(sum(pnls) / total, 4) if total > 0 else 0,
    }


def cmd_batch(trade_ids, tag):
    for tid in trade_ids:
        cmd_add(tid, tag)
    return {"ok": True, "tagged_count": len(trade_ids), "tag": tag}


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    p_add = sub.add_parser("add")
    p_add.add_argument("trade_id")
    p_add.add_argument("tag")

    p_rem = sub.add_parser("remove")
    p_rem.add_argument("trade_id")
    p_rem.add_argument("tag")

    sub.add_parser("list")

    p_stats = sub.add_parser("stats")
    p_stats.add_argument("tag")
    p_stats.add_argument("--trades", default="[]")

    p_batch = sub.add_parser("batch")
    p_batch.add_argument("--trade-ids", required=True)
    p_batch.add_argument("--tag", required=True)

    args = parser.parse_args()

    if args.cmd == "add":
        result = cmd_add(args.trade_id, args.tag)
    elif args.cmd == "remove":
        result = cmd_remove(args.trade_id, args.tag)
    elif args.cmd == "list":
        result = cmd_list()
    elif args.cmd == "stats":
        result = cmd_stats(args.tag, args.trades)
    elif args.cmd == "batch":
        ids = json.loads(args.trade_ids)
        result = cmd_batch(ids, args.tag)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
