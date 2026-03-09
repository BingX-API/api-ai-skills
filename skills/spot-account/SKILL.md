---
name: bingx-spot-account
description: BingX spot account management — query account balance, manage assets, and transfer funds between accounts. Use when the user asks about BingX spot account balance, asset overview, asset transfers, or fund account operations.
---

# BingX Spot Account

Authenticated endpoints for BingX spot trading and account management. All endpoints require HMAC SHA256 signature authentication.

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

---

## Quick Reference

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/openApi/spot/v1/account/balance` | GET | Query spot account assets/balance | Yes |
| `/openApi/fund/v1/account/balance` | GET | Query fund account balance | Yes |
| `/openApi/account/v1/allAccountBalance` | GET | Asset overview (all account types) | Yes |
| `/openApi/api/asset/v1/transfer` | POST | Transfer assets between accounts | Yes |
| `/openApi/api/v3/asset/transfer` | GET | Query asset transfer records | Yes |
| `/openApi/api/v3/asset/transferRecord` | GET | Query asset transfer records (new format) | Yes |
| `/openApi/api/asset/v1/transfer/supportCoins` | GET | Query supported coins for transfer | Yes |
| `/openApi/wallets/v1/capital/innerTransfer/apply` | POST | Internal P2P transfer between accounts | Yes |
| `/openApi/wallets/v1/capital/innerTransfer/records` | GET | Main account internal transfer records | Yes |

---

## Parameters

### Order Parameters

* **symbol**: Trading pair in `BASE-QUOTE` format (e.g., `BTC-USDT`, `ETH-USDT`)
* **side**: Order direction — `BUY` or `SELL`
* **type**: Order type (see Enums)
* **quantity**: Order quantity in base asset (e.g., `0.1` for BTC-USDT)
* **quoteOrderQty**: Order amount in quote asset (e.g., `100` USDT); `quantity` takes priority if both are provided
* **price**: Limit price (required for `LIMIT` type)
* **stopPrice**: Trigger price (required for `TAKE_STOP_LIMIT`, `TAKE_STOP_MARKET`, `TRIGGER_LIMIT`, `TRIGGER_MARKET` types)
* **timeInForce**: `GTC` | `IOC` | `FOK` | `PostOnly` — default `GTC`; required for `LIMIT` type
* **newClientOrderId**: Custom order ID, 1–40 chars
* **recvWindow**: Request validity window in milliseconds (max 60000)
* **orderId**: System order ID (for cancel/query operations)
* **clientOrderID**: Custom order ID (for cancel/query operations)

### Account Parameters

* **asset** / **coin**: Asset name (e.g., `USDT`, `BTC`)
* **amount**: Transfer amount
* **type** (transfer): Transfer direction (see TransferType enum)
* **accountType**: Account type for asset overview (see AccountType enum)

### Enums

**type** (Order type):
- `MARKET` — Market order (fills immediately at best available price)
- `LIMIT` — Limit order (requires `price` and `timeInForce`)
- `TAKE_STOP_LIMIT` — Take-profit/stop-loss limit order (requires `stopPrice` and `price`)
- `TAKE_STOP_MARKET` — Take-profit/stop-loss market order (requires `stopPrice`)
- `TRIGGER_LIMIT` — Trigger limit order (requires `stopPrice` and `price`)
- `TRIGGER_MARKET` — Trigger market order (requires `stopPrice`)

**side**: `BUY` | `SELL`

**timeInForce**: `GTC` | `IOC` | `FOK` | `PostOnly`

**TransferType** (asset transfer direction):
- `FUND_SFUTURES` — Funding Account → Standard Contract
- `SFUTURES_FUND` — Standard Contract → Funding Account
- `FUND_PFUTURES` — Funding Account → Perpetual Futures
- `PFUTURES_FUND` — Perpetual Futures → Funding Account
- `SFUTURES_PFUTURES` — Standard Contract → Perpetual Futures
- `PFUTURES_SFUTURES` — Perpetual Futures → Standard Contract

**CancelReplaceMode**:
- `STOP_ON_FAILURE` — Abort the new order if cancel fails
- `ALLOW_FAILURE` — Place the new order even if cancel fails

**cancelRestrictions** (restrict cancellation by status):
- `NEW` — Cancel only new orders
- `PENDING` — Cancel only pending orders
- `PARTIALLY_FILLED` — Cancel only partially-filled orders

**AccountType** (for asset overview):
- `sopt` — Spot (fund account)
- `stdFutures` — Standard futures
- `coinMPerp` — Coin-margined perpetual
- `USDTMPerp` — USDT-margined perpetual
- `copyTrading` — Copy trading
- `grid` — Grid trading
- `eran` — Wealth management
- `c2c` — C2C account

### Parameter Validation Rules

* **symbol**: Must match `^[A-Z0-9]+-[A-Z]+$`; max 20 characters (e.g., `BTC-USDT`)
* **quantity**: Must be a positive number (> 0); precision depends on the symbol
* **quoteOrderQty**: When provided, must be a positive number (> 0)
* **price**: When provided, must be a positive number (> 0)
* **stopPrice**: When provided, must be a positive number (> 0)
* **newClientOrderId**: 1–40 characters; avoid special characters
* **amount**: Must be a positive number (> 0) for transfers
* **type**: Must exactly match one of the `TransferType` enum values
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

**Query spot account balance:**

```typescript
const balance = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/spot/v1/account/balance"
);
// balance.balances[].asset, balance.balances[].free, balance.balances[].locked
```

**Query fund account balance:**

```typescript
const fundBalance = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/fund/v1/account/balance"
);
// fundBalance.data.balance
```

**Query all account balances (overview):**

```typescript
const allBalances = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/account/v1/allAccountBalance"
);
// allBalances[].asset, allBalances[].balance
```

**Transfer assets (Spot → Perpetual Futures):**

```typescript
await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/api/asset/v1/transfer", {
    type: "FUND_PFUTURES",
    asset: "USDT",
    amount: 100,
  }
);
```

**Query asset transfer records:**

```typescript
const transfers = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/api/v3/asset/transferRecord", {
    type: "FUND_PFUTURES",
    startTime: 1700000000000,
    endTime: 1702731787011,
  }
);
// transfers[].asset, transfers[].amount, transfers[].type, transfers[].timestamp
```

**Query supported coins for transfer:**

```typescript
const coins = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/api/asset/v1/transfer/supportCoins"
);
// coins[].coin, coins[].name
```

## Additional Resources

For full parameter descriptions, response schemas, and all 9 endpoints, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

Asset transfer operations require **CONFIRM** on `prod-live`. Read-only queries (balance, transfer records) do not.

- **prod-live**: Ask user to type **CONFIRM** before any asset transfer.
- **prod-vst**: No CONFIRM required. Inform user: "You are operating in the Production Simulated (VST) environment."

### Step 1 — Identify the Operation

If the user's intent is unclear, present options:

> What would you like to do?
> - Check account balance (spot / fund / all accounts)
> - Transfer assets between accounts
> - Query transfer records
> - Query supported coins for transfer
> - Internal P2P transfer

### Step 2 — Account Balance Query

For balance queries, ask which account type:
> Which account balance would you like to check?
> - Spot account balance
> - Fund account balance
> - All accounts overview

### Step 3 — Asset Transfer Flow

1. Ask which direction:
   > Transfer direction:
   > - Spot → Perpetual Futures (FUND_PFUTURES)
   > - Perpetual Futures → Spot (PFUTURES_FUND)
   > - Spot → Standard Contract (FUND_SFUTURES)
   > - Standard Contract → Spot (SFUTURES_FUND)
   > - Standard Contract → Perpetual Futures (SFUTURES_PFUTURES)
   > - Perpetual Futures → Standard Contract (PFUTURES_SFUTURES)
2. Ask for `asset` (e.g., USDT) and `amount`.
3. For `prod-live`: ask for **CONFIRM**.
4. Execute POST `/openApi/api/asset/v1/transfer`.

### Step 4 — Transfer Records Query

1. Optionally ask for `type` (transfer direction) and time range.
2. Execute GET `/openApi/api/v3/asset/transferRecord`.
3. Present results in a table format: asset, amount, type, timestamp, status.
