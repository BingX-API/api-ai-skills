---
name: bingx-swap-account
description: Query BingX perpetual swap account data including balance, positions, commission rates, and fund flow history. Use when the user asks about BingX account balance, margin info, current positions, PnL, liquidation price, fee rates, or income/fund flow records.
---

# BingX Swap Account

Authenticated read-only endpoints for BingX perpetual futures account data. All endpoints require HMAC SHA256 signature authentication.

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

---

## Quick Reference

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/openApi/swap/v3/user/balance` | GET | Account balance, equity, and margin info | Yes |
| `/openApi/swap/v2/user/positions` | GET | Current open positions with PnL and liquidation price | Yes |
| `/openApi/swap/v2/user/commissionRate` | GET | User taker/maker fee rates | Yes |
| `/openApi/swap/v2/user/income` | GET | Fund flow history (PnL, funding fees, trading fees, etc.) | Yes |
| `/openApi/swap/v2/user/income/export` | GET | Export fund flow as Excel file | Yes |

---

## Parameters

### Common Parameters

* **symbol**: Trading pair in `BASE-QUOTE` format (e.g., `BTC-USDT`). Optional for most account endpoints.
* **timestamp**: Request timestamp in milliseconds (required for all authenticated endpoints).
* **recvWindow**: Request validity window in milliseconds (optional, max 60000).
* **startTime** / **endTime**: Time range filters in milliseconds (used by income endpoints).
* **limit**: Number of results to return (used by income endpoints; default 100, max 1000).

### incomeType Enum (for income endpoints)

| Value | Description |
|-------|-------------|
| `TRANSFER` | Transfer |
| `REALIZED_PNL` | Realized profit and loss |
| `FUNDING_FEE` | Funding fee |
| `TRADING_FEE` | Trading fee |
| `INSURANCE_CLEAR` | Liquidation |
| `TRIAL_FUND` | Trial fund |
| `ADL` | Auto-deleveraging |
| `SYSTEM_DEDUCTION` | System deduction |
| `GTD_PRICE` | Guaranteed price |

### Parameter Validation Rules

* **symbol**: When provided, must match `^[A-Z0-9]+-[A-Z]+$`; max 20 characters (e.g., `BTC-USDT`)
* **incomeType**: When provided, must exactly match one of the enum values above
* **startTime** / **endTime**: Unix timestamps in milliseconds; `endTime` must be ≥ `startTime`
* **limit**: Positive integer, 1–1000; default 100
* **recvWindow**: Integer, 1–5000 ms (see [Replay Protection](../references/authentication.md#replay-protection))
* **timestamp**: Unix time in milliseconds; must be within `recvWindow` of server time

---

## Quick Start

```typescript
import * as crypto from "crypto";
// Full signing details & edge cases → references/authentication.md
const BASE = {
  "prod-live": ["https://open-api.bingx.com", "https://open-api.bingx.pro"],
  "prod-vst":  ["https://open-api-vst.bingx.com", "https://open-api-vst.bingx.pro"],
};
async function fetchSigned(env: string, apiKey: string, secretKey: string,
  method: "GET" | "POST" | "DELETE", path: string, params: Record<string, unknown> = {}
) {
  const urls = BASE[env] ?? BASE["prod-live"];
  const all = { ...params, timestamp: Date.now() };
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
      });
      const json = await res.json();
      if (json.code !== 0) throw new Error(`BingX error ${json.code}: ${json.msg}`);
      return json.data;
    } catch (e) {
      if (base === urls[urls.length - 1]) throw e;
    }
  }
}
```

---

## Common Calls

**Query account balance:**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v3/user/balance"
);
// data.balance.balance, data.balance.equity, data.balance.availableMargin
```

**Query all open positions:**

```typescript
const positions = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/user/positions"
);
// positions[].symbol, positions[].positionAmt, positions[].unrealizedProfit, positions[].liquidationPrice
```

**Query positions for a specific symbol:**

```typescript
const positions = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/user/positions", { symbol: "BTC-USDT" }
);
```

**Query user fee rates:**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/user/commissionRate"
);
// data.commission.takerCommissionRate, data.commission.makerCommissionRate
```

**Query recent fund flow (last 7 days, all types):**

```typescript
const income = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/user/income", { limit: 100 }
);
// income[].incomeType, income[].income, income[].asset, income[].time
```

**Query funding fees for BTC-USDT in a time range:**

```typescript
const income = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/swap/v2/user/income", {
    symbol: "BTC-USDT",
    incomeType: "FUNDING_FEE",
    startTime: 1700000000000,
    endTime: 1702731787011,
    limit: 200,
  }
);
```

## Additional Resources

For complete parameter descriptions and full response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

All swap-account endpoints are **read-only** (GET). No CONFIRM required for any environment — they never modify account state.

Credentials are required. If no account is specified, default to the `main` account.

### Step 1 — Identify the query

If the user's intent is unclear, present options:

> Please select the account information type to query:
> - Account balance / Equity / Margin — balance
> - Current positions / Unrealized PnL / Liquidation price — positions
> - Commission rate — commissionRate
> - Fund flow (PnL / funding fee / trading fee / etc.) — income
> - Export fund flow (Excel) — income/export

### Step 2 — Collect symbol (if relevant)

For `positions` and `income` endpoints, symbol is optional. If the user asks about a specific coin, infer the symbol automatically (e.g., "BTC position" → `BTC-USDT`).

If not specified, query all symbols and inform the user.

### Step 3 — Collect time range (for income endpoints)

- If neither `startTime` nor `endTime` is provided, the API returns the **last 7 days** of data. Inform the user.
- Only the last **3 months** of data is available.
- If the user asks for a specific date range, convert to milliseconds.

### Step 4 — Collect incomeType (for income endpoints)

If the user specifies a type (e.g., "funding fee", "trading fee", "PnL"), map to the correct `incomeType` enum value:

| User says | incomeType |
|-----------|------------|
| Realized PnL / PnL | `REALIZED_PNL` |
| Funding fee / Funding rate | `FUNDING_FEE` |
| Trading fee / Commission | `TRADING_FEE` |
| Liquidation | `INSURANCE_CLEAR` |
| ADL / Auto-deleverage | `ADL` |
| Transfer | `TRANSFER` |

If not specified, omit `incomeType` to return all types.

### Step 5 — Execute and report

Execute the API call and present results in a readable format:

- **balance**: Show equity, available margin, used margin, unrealized PnL as a summary table.
- **positions**: Show a table per position: symbol, side, amount, avg price, unrealized PnL, liquidation price, leverage.
- **commissionRate**: Show taker and maker rate as percentages (multiply by 100).
- **income**: Show a table of recent records: time, type, symbol, amount, asset.
