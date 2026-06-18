import json, argparse, sys, os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams["font.family"] = ["Arial Unicode MS", "DejaVu Sans"]


def parse_period(period: str, trades_df: pd.DataFrame):
    now = pd.Timestamp.now(tz="UTC")
    if period == "all":
        return trades_df
    days = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}.get(period, 7)
    cutoff = now - pd.Timedelta(days=days)
    if "closeTime" in trades_df.columns:
        trades_df["close_dt"] = pd.to_datetime(trades_df["closeTime"], unit="ms", utc=True)
        return trades_df[trades_df["close_dt"] >= cutoff]
    return trades_df


def calc_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"error": "No trades found in the selected period"}

    pnl_col = next((c for c in ["realizedPnl", "pnl", "profit"] if c in df.columns), None)
    fee_col = next((c for c in ["fee", "commission"] if c in df.columns), None)
    dir_col = next((c for c in ["positionSide", "side", "direction"] if c in df.columns), None)

    if pnl_col:
        df[pnl_col] = pd.to_numeric(df[pnl_col], errors="coerce").fillna(0.0)
    if fee_col:
        df[fee_col] = pd.to_numeric(df[fee_col], errors="coerce").fillna(0.0)
    pnls = df[pnl_col] if pnl_col else pd.Series([0.0] * len(df))
    fees = df[fee_col] if fee_col else pd.Series([0.0] * len(df))

    wins = (pnls > 0).sum()
    losses = (pnls <= 0).sum()
    total = len(pnls)

    profit_sum = pnls[pnls > 0].sum()
    loss_sum = abs(pnls[pnls < 0].sum())
    profit_factor = round(profit_sum / loss_sum, 2) if loss_sum > 0 else float("inf")

    cumulative = pnls.cumsum()
    rolling_max = cumulative.cummax()
    drawdown = cumulative - rolling_max
    max_drawdown = round(float(drawdown.min()), 4)

    # Sharpe ratio (simplified per-trade calculation)
    daily_pnl = pnls
    sharpe = round(float(daily_pnl.mean() / daily_pnl.std()), 2) if daily_pnl.std() > 0 else 0

    # Long/short breakdown
    long_win_rate = short_win_rate = long_pnl = short_pnl = long_count = short_count = 0
    if dir_col:
        long_mask = df[dir_col].str.upper().isin(["LONG", "BUY"])
        short_mask = df[dir_col].str.upper().isin(["SHORT", "SELL"])
        long_pnls = pnls[long_mask]
        short_pnls = pnls[short_mask]
        long_count = len(long_pnls)
        short_count = len(short_pnls)
        long_win_rate = round((long_pnls > 0).sum() / len(long_pnls) * 100, 1) if long_count > 0 else 0
        short_win_rate = round((short_pnls > 0).sum() / len(short_pnls) * 100, 1) if short_count > 0 else 0
        long_pnl = round(float(long_pnls.sum()), 4)
        short_pnl = round(float(short_pnls.sum()), 4)

    # Per-symbol breakdown
    sym_col = next((c for c in ["symbol", "coin"] if c in df.columns), None)
    best_symbol = worst_symbol = best_pnl = worst_pnl = None
    if sym_col:
        sym_pnl = df.groupby(df[sym_col])[pnl_col].sum() if pnl_col else None
        if sym_pnl is not None and not sym_pnl.empty:
            best_symbol = sym_pnl.idxmax()
            worst_symbol = sym_pnl.idxmin()
            best_pnl = round(float(sym_pnl.max()), 4)
            worst_pnl = round(float(sym_pnl.min()), 4)

    return {
        "total_trades": int(total),
        "wins": int(wins),
        "losses": int(losses),
        "win_rate": round(float(wins / total * 100), 1) if total > 0 else 0,
        "total_pnl": round(float(pnls.sum()), 4),
        "avg_pnl": round(float(pnls.mean()), 4),
        "max_win": round(float(pnls.max()), 4),
        "max_loss": round(float(pnls.min()), 4),
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe,
        "long_count": int(long_count),
        "short_count": int(short_count),
        "long_win_rate": long_win_rate,
        "short_win_rate": short_win_rate,
        "long_pnl": long_pnl,
        "short_pnl": short_pnl,
        "best_symbol": best_symbol,
        "worst_symbol": worst_symbol,
        "best_pnl": best_pnl,
        "worst_pnl": worst_pnl,
        "total_fees": round(float(fees.sum()), 4),
        "pnl_series": pnls.tolist(),
    }


def generate_charts(df: pd.DataFrame, stats: dict, output_dir: str):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    generated = []

    pnl_col = next((c for c in ["realizedPnl", "pnl", "profit"] if c in df.columns), None)
    if not pnl_col:
        return generated

    pnls = df[pnl_col].astype(float)

    # PnL curve
    fig, ax = plt.subplots(figsize=(10, 4))
    cumulative = pnls.cumsum()
    ax.plot(cumulative.values, color="#2196F3")
    ax.fill_between(range(len(cumulative)), cumulative.values, alpha=0.1, color="#2196F3")
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_title("Cumulative PnL")
    ax.set_xlabel("Trade #")
    ax.set_ylabel("PnL (USDT)")
    plt.tight_layout()
    path = out / "pnl_curve.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    generated.append(str(path))

    # Win/loss distribution
    fig, ax = plt.subplots(figsize=(10, 4))
    colors = ["#4CAF50" if p > 0 else "#F44336" for p in pnls]
    ax.bar(range(len(pnls)), pnls.values, color=colors, width=0.8)
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_title("Win/Loss Distribution")
    ax.set_xlabel("Trade #")
    ax.set_ylabel("PnL (USDT)")
    plt.tight_layout()
    path = out / "win_loss_dist.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    generated.append(str(path))

    # Symbol breakdown
    sym_col = next((c for c in ["symbol", "coin"] if c in df.columns), None)
    if sym_col:
        sym_pnl = df.groupby(df[sym_col])[pnl_col].sum().astype(float)
        if len(sym_pnl) > 0:
            fig, ax = plt.subplots(figsize=(7, 7))
            colors_pie = ["#4CAF50" if v > 0 else "#F44336" for v in sym_pnl.values]
            ax.pie(sym_pnl.abs(), labels=sym_pnl.index, colors=colors_pie, autopct="%1.1f%%")
            ax.set_title("PnL by Symbol")
            plt.tight_layout()
            path = out / "symbol_breakdown.png"
            fig.savefig(path, dpi=120)
            plt.close(fig)
            generated.append(str(path))

    # Long vs short comparison
    dir_col = next((c for c in ["positionSide", "side", "direction"] if c in df.columns), None)
    if dir_col and stats.get("long_count", 0) + stats.get("short_count", 0) > 0:
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        categories = ["Long", "Short"]
        win_rates = [stats["long_win_rate"], stats["short_win_rate"]]
        pnls_ls = [stats["long_pnl"], stats["short_pnl"]]
        axes[0].bar(categories, win_rates, color=["#2196F3", "#FF9800"])
        axes[0].set_title("Win Rate %")
        axes[0].set_ylim(0, 100)
        bar_colors = ["#4CAF50" if p > 0 else "#F44336" for p in pnls_ls]
        axes[1].bar(categories, pnls_ls, color=bar_colors)
        axes[1].set_title("Total PnL (USDT)")
        plt.tight_layout()
        path = out / "long_short_compare.png"
        fig.savefig(path, dpi=120)
        plt.close(fig)
        generated.append(str(path))

    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="summary")
    parser.add_argument("--period", default="7d")
    parser.add_argument("--symbol", default="all")
    parser.add_argument("--trades", required=True)
    parser.add_argument("--output-dir", default=str(Path.home() / ".bingx-skills" / "trade-review" / "charts"))
    parser.add_argument("--compare-period", default=None)
    args = parser.parse_args()

    raw = json.loads(args.trades)
    if not raw:
        print(json.dumps({"error": "No trade records found"}))
        sys.exit(0)

    df = pd.DataFrame(raw)

    # Time filter
    df_filtered = parse_period(args.period, df.copy())
    if args.symbol != "all":
        sym_col = next((c for c in ["symbol", "coin"] if c in df_filtered.columns), None)
        if sym_col:
            df_filtered = df_filtered[df_filtered[sym_col].str.upper() == args.symbol.upper()]

    if df_filtered.empty:
        print(json.dumps({"error": "No trades found matching the selected filters"}))
        sys.exit(0)

    stats = calc_stats(df_filtered)

    if args.mode == "compare" and args.compare_period:
        df_prev = parse_period(args.compare_period, df.copy())
        stats_prev = calc_stats(df_prev)
        result = {"current": stats, "previous": stats_prev, "period": args.period, "compare_period": args.compare_period}
    else:
        charts = generate_charts(df_filtered, stats, args.output_dir)
        stats.pop("pnl_series", None)
        result = {"stats": stats, "charts": charts, "output_dir": args.output_dir}

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
