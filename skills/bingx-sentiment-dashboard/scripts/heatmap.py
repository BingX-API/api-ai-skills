"""Funding rate heatmap generation (seaborn)"""
import json, argparse, sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--funding", required=True)
    parser.add_argument("--output", default="/tmp/funding_heatmap.png")
    args = parser.parse_args()

    funding = json.loads(args.funding)
    if not funding:
        print(json.dumps({"error": "Funding rate data is empty"}))
        sys.exit(1)

    # top 30 symbols by absolute funding rate
    records = []
    for item in funding:
        symbol = item.get("symbol", "")
        rate = float(item.get("lastFundingRate") or item.get("fundingRate") or 0)
        records.append({"symbol": symbol, "rate": rate})

    df = pd.DataFrame(records)
    if df.empty:
        print(json.dumps({"error": "No valid funding rate data"}))
        sys.exit(1)

    df["abs_rate"] = df["rate"].abs()
    df = df.sort_values("abs_rate", ascending=False).head(30).drop(columns=["abs_rate"])

    # build heatmap matrix (single column, current rate)
    matrix = df.set_index("symbol")[["rate"]]
    matrix.columns = ["Funding Rate"]

    fig, ax = plt.subplots(figsize=(4, max(8, len(matrix) * 0.35)))
    sns.heatmap(
        matrix,
        ax=ax,
        cmap=sns.diverging_palette(130, 10, as_cmap=True),
        center=0,
        annot=True,
        fmt=".4f",
        linewidths=0.5,
        cbar_kws={"label": "Funding Rate"},
    )
    ax.set_title("Funding Rate Heatmap (Top 30)", fontsize=12, pad=12)
    ax.set_ylabel("")
    plt.tight_layout()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=120)
    plt.close(fig)

    print(json.dumps({"ok": True, "path": str(out), "symbols": len(matrix)}))


if __name__ == "__main__":
    main()
