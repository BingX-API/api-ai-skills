"""Local storage manager, persists trades.json to ~/.bingx-skills/trade-review/"""
import json, os
from pathlib import Path

DATA_DIR = Path.home() / ".bingx-skills" / "trade-review"
TRADES_FILE = DATA_DIR / "trades.json"


def ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load() -> dict:
    ensure_dir()
    if not TRADES_FILE.exists():
        return {}
    with open(TRADES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data: dict):
    ensure_dir()
    with open(TRADES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_trade(trade_id: str) -> dict:
    data = load()
    return data.get(trade_id, {})


def upsert_trade(trade_id: str, fields: dict):
    data = load()
    if trade_id not in data:
        data[trade_id] = {"trade_id": trade_id, "tags": [], "reflection": "", "created_at": ""}
    data[trade_id].update(fields)
    save(data)


def merge_with_api(api_trades: list) -> list:
    local = load()
    result = []
    for t in api_trades:
        tid = str(t.get("tradeId") or t.get("orderId") or t.get("id", ""))
        local_data = local.get(tid, {})
        t["tags"] = local_data.get("tags", [])
        t["reflection"] = local_data.get("reflection", "")
        result.append(t)
    return result
