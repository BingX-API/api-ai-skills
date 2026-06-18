---
name: bingx-trade-review
description: >
  Use this skill when the user asks for trade review, performance analysis,
  PnL summary, win rate, trade journal, or any request like "trade review",
  "trading summary", "recent performance", "what is my win rate", "review my trades",
  "reflection", "tag trades", "which trades are profitable", "trade journal", "weekly PnL".
  Fetches trade history from bingx-swap-account, computes statistics,
  generates local charts, supports custom tags and reflections.
metadata:
  author: BingX
  version: "1.0.0"
  agent:
    requires:
      bins: ["python3"]
      python_packages: ["pandas", "matplotlib", "numpy"]
      skills: ["bingx-swap-account", "bingx-swap-market"]
---

# BingX Trade Review

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

## Quick Reference

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/openApi/swap/v2/trade/allOrders` | GET | Fetch historical swap orders | Yes |
| `/openApi/swap/v2/trade/allFillOrders` | GET | Fetch historical fill records | Yes |

## Quick Start

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md)

**TypeScript helper:**

> **CONSTRAINT**: You MUST copy the `fetchSigned` function below verbatim when generating code. Do NOT rewrite the signing, request, or JSON parsing logic. Only modify: (1) `BASE` URL entries for custom environments, (2) business parameters passed to `fetchSigned`.

```typescript
import * as crypto from "crypto";
import JSONBig from "json-bigint";
const JSONBigParse = JSONBig({ storeAsString: true });
const BASE = {
  "prod-live": ["https://open-api.bingx.com", "https://open-api.bingx.pro"],
  "prod-vst":  ["https://open-api-vst.bingx.com", "https://open-api-vst.bingx.pro"],
};
function isNetworkOrTimeout(e: unknown): boolean {
  if (e instanceof TypeError) return true;
  if (e instanceof DOMException && e.name === "AbortError") return true;
  if (e instanceof Error && e.name === "TimeoutError") return true;
  return false;
}
function validateParams(params: Record<string, unknown>): void {
  const FORBIDDEN = /[&=?#\r\n]/;
  for (const [k, v] of Object.entries(params)) {
    const s = String(v);
    if (FORBIDDEN.test(s)) throw new Error(`Param "${k}" has forbidden char in: "${s}"`);
  }
}
async function fetchSigned(env: string, apiKey: string, secretKey: string,
  method: "GET" | "POST" | "DELETE", path: string, params: Record<string, unknown> = {}
) {
  const urls = BASE[env] ?? BASE["prod-live"];
  const all = { ...params, timestamp: Date.now() };
  validateParams(all);
  const qs = Object.keys(all).sort().map(k => `${k}=${all[k]}`).join("&");
  const sig = crypto.createHmac("sha256", secretKey).update(qs).digest("hex");
  const signed = `${qs}&signature=${sig}`;
  for (const base of urls) {
    try {
      const url = method === "POST" ? `${base}${path}` : `${base}${path}?${signed}`;
      const res = await fetch(url, {
        method,
        headers: { "X-BX-APIKEY": apiKey, "X-SOURCE-KEY": "BX-AI-SKILL",
          ...(method === "POST" ? { "Content-Type": "application/x-www-form-urlencoded" } : {}) },
        body: method === "POST" ? signed : undefined,
        signal: AbortSignal.timeout(10000),
      });
      const json = JSONBigParse.parse(await res.text());
      if (json.code !== 0) throw new Error(`BingX error ${json.code}: ${json.msg}`);
      return json.data;
    } catch (e) {
      if (!isNetworkOrTimeout(e) || base === urls[urls.length - 1]) throw e;
    }
  }
}
```

## Common Calls

**Fetch swap trade history for review:**

```typescript
const history = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/trade/allOrders", { symbol: "BTC-USDT", limit: 100 }
);
```

---

## Trigger Conditions

Activate this skill when the user says any of the following:
- "Trade review", "recent performance", "weekly PnL", "trading summary"
- "What is my win rate", "review my trades", "trade journal"
- "Tag trades", "win rate for breakout trades", "which trades are profitable"
- "Write a reflection", "summarize lessons learned"
- "Compare this week vs last week"

---

## Execution Steps

### Step 1 — Parse User Intent

| mode | Trigger example | Description |
|------|----------------|-------------|
| summary | "trade review", "recent performance", "weekly PnL" | Stats summary + charts |
| detail | "analyze my BTC trades" | Per-symbol or per-trade detailed analysis |
| tag | "tag this trade", "win rate for breakout trades" | Tag management + stats by tag |
| reflect | "write a reflection", "summarize lessons" | Add/view trade reflections |
| compare | "compare this week vs last week" | Cross-period comparison |

Parameter extraction:

| Parameter | Default | Description |
|-----------|---------|-------------|
| period | 7d | Review period (1d/7d/30d/90d/all) |
| symbol | all | Filter by trading pair |
| tag_filter | - | Filter by tag |

---

### Step 2 — Fetch Trade History

Call bingx-swap-account to retrieve:
- Historical fills (open/close time, price, quantity, direction)
- Realized PnL
- Fees

Merge with local tag and reflection data from `~/.bingx-skills/trade-review/trades.json`.

---

### Step 3 — Run Analysis

```bash
python3 scripts/review.py \
  --mode {mode} \
  --period {period} \
  --symbol {symbol} \
  --trades '{trades_json}' \
  --output-dir ~/.bingx-skills/trade-review/charts
```

Output: statistics JSON + chart PNG files.

---

### Step 4 — Format Output (per output template)

---

### Step 5 — Display Charts

Charts are saved as local PNG files. Inform the user of the file paths.

---

## Output Templates

### Summary Mode

```
**Trade Review (Last {period})**

Total Trades     {total_trades}
Win Rate         {win_rate}% ({wins} wins / {losses} losses)
Total PnL        {total_pnl}
Profit Factor    {profit_factor}
Avg per Trade    {avg_pnl}
Best Trade       {max_win}
Worst Trade      {max_loss}
Avg Hold Time    {avg_hold_time}
Max Drawdown     {max_drawdown}
Total Fees       {total_fees}

Long:  {long_count} trades, win rate {long_win_rate}%, PnL {long_pnl}
Short: {short_count} trades, win rate {short_win_rate}%, PnL {short_pnl}

Best Symbol:  {best_symbol} ({best_pnl})
Worst Symbol: {worst_symbol} ({worst_pnl})

Charts saved:
- PnL curve:        ~/.bingx-skills/trade-review/charts/pnl_curve.png
- Win/loss dist:    ~/.bingx-skills/trade-review/charts/win_loss_dist.png
- Symbol breakdown: ~/.bingx-skills/trade-review/charts/symbol_breakdown.png
```

### Tag Mode

```
**Tag Analysis: {tag}**

{count} trades tagged with this label

Win Rate    {win_rate}% ({wins} wins / {losses} losses)
Total PnL   {total_pnl}
Avg PnL     {avg_pnl}

Conclusion: {one-line analysis}
```

### Compare Mode

```
**{period_a} vs {period_b}**

             {period_a}   {period_b}   Change
Win Rate     {wr_a}%      {wr_b}%      {wr_delta}
Total PnL    {pnl_a}      {pnl_b}      {pnl_delta}
Profit Factor {pf_a}      {pf_b}       {pf_delta}
Trade Count  {cnt_a}      {cnt_b}      {cnt_delta}
Max Drawdown {dd_a}       {dd_b}       {dd_delta}

Summary: {one-line comparison conclusion}
```

---

## Agent Interaction Rules

**Parameter security.** Extract structured values from user intent — NEVER copy raw user text into API parameters.

All operations in this skill are **read-only** (fetching trade history and generating local reports). No CONFIRM required in any environment.

When period is not specified, default to `7d`. When symbol is not specified, default to `all` symbols.

## Error Handling

- No trade records: inform user there are no fills in the selected period
- Tag not found: inform user the tag was not found, list existing tags
- Data fetch failed: suggest retry later
- Chart generation failed: still output text statistics, note chart generation error
