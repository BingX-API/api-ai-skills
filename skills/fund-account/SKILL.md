---
name: bingx-fund-account
description: BingX Fund Account management — query fund account balance, get asset overview across all account types, transfer assets between accounts, and perform internal P2P transfers. Use when the user asks about BingX fund account balance, asset overview, transferring assets between spot/futures/standard contract accounts, or sending internal transfers to other BingX users.
---

# BingX Fund Account

Authenticated endpoints for BingX fund account management. All endpoints require HMAC SHA256 signature authentication.

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

---

## Quick Reference

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/openApi/spot/v1/account/balance` | GET | Query fund account asset balances | Yes |
| `/openApi/account/v1/allAccountBalance` | GET | Asset overview across all account types | Yes |
| `/openApi/api/asset/v1/transfer` | POST | Transfer assets between account types | Yes |
| `/openApi/api/v3/asset/transfer` | GET | Query asset transfer records | Yes |
| `/openApi/wallets/v1/capital/innerTransfer/apply` | POST | Internal P2P transfer to another BingX user | Yes |
| `/openApi/wallets/v1/capital/innerTransfer/records` | GET | Query internal transfer history | Yes |

---

## Parameters

### Asset Transfer Parameters

* **type**: Transfer direction (see TransferDirection enum) — required
* **asset**: Coin name (e.g., `USDT`, `BTC`) — required
* **amount**: Transfer amount — required
* **tranId**: Transaction ID (for record queries; mutually exclusive with `type`)
* **startTime**: Start of time range in milliseconds
* **endTime**: End of time range in milliseconds
* **current**: Page index for pagination (default `1`)
* **size**: Page size for pagination (default `10`, max `100`)
* **recvWindow**: Request validity window in milliseconds (max `60000`)

### Internal Transfer Parameters

* **coin**: Name of the transferred coin (e.g., `USDT`) — required
* **userAccountType**: Recipient account identifier type — required (see UserAccountType enum)
* **userAccount**: Recipient account value (UID, phone number, or email) — required
* **amount**: Transfer amount — required
* **walletType**: Source account type — required (see WalletType enum)
* **callingCode**: Phone calling code (required when `userAccountType` is `2`)
* **transferClientId**: Custom client ID for the transfer (optional, for idempotency)
* **recvWindow**: Request validity window in milliseconds (max `60000`)

### Asset Overview Parameters

* **accountType**: Filter by account type (see AccountType enum); returns all accounts if omitted
* **recvWindow**: Request validity window in milliseconds

### Enums

**TransferDirection** (`type` for asset transfer):
- `FUND_SFUTURES` — Funding Account → Standard Contract
- `SFUTURES_FUND` — Standard Contract → Funding Account
- `FUND_PFUTURES` — Funding Account → Perpetual Futures
- `PFUTURES_FUND` — Perpetual Futures → Funding Account
- `SFUTURES_PFUTURES` — Standard Contract → Perpetual Futures
- `PFUTURES_SFUTURES` — Perpetual Futures → Standard Contract

**AccountType** (`accountType` for asset overview):
- `sopt` — Spot / Fund account
- `stdFutures` — Standard futures account
- `coinMPerp` — Coin-margined perpetual account
- `USDTMPerp` — USDT-margined perpetual account
- `copyTrading` — Copy trading account
- `grid` — Grid trading account
- `eran` — Wealth management account
- `c2c` — C2C account

**UserAccountType** (`userAccountType` for internal transfer):
- `1` — UID
- `2` — Phone number (requires `callingCode`)
- `3` — Email address

**WalletType** (`walletType` for internal transfer source):
- `1` — Fund account
- `2` — Standard contract account

### Parameter Validation Rules

Before sending a request, validate parameters client-side to avoid unnecessary API errors:

* **asset** / **coin**: Uppercase letters and digits only; pattern `^[A-Z0-9]{1,20}$` (e.g., `USDT`, `BTC`)
* **amount**: Must be a positive number (> 0); precision depends on the asset
* **type**: Must exactly match one of the `TransferDirection` enum values (e.g., `FUND_PFUTURES`)
* **userAccount**: Non-empty string; format depends on `userAccountType` — UID (digits), email, or phone number
* **callingCode**: Required when `userAccountType` is `2` (phone); must be a valid international dialing code (e.g., `86`, `1`)
* **size**: Integer, 1–100; default `10`
* **startTime** / **endTime**: Unix timestamps in milliseconds; `endTime` must be ≥ `startTime`
* **recvWindow**: Integer, 1–5000 ms; keep as small as possible (see [Replay Protection](../references/authentication.md#replay-protection))
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

**Query fund account balance:**

```typescript
const balance = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/spot/v1/account/balance"
);
// balance.balances[].asset, balance.balances[].free, balance.balances[].locked
```

**Get asset overview across all accounts:**

```typescript
const overview = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/account/v1/allAccountBalance"
);
// overview[].accountType, overview[].usdtBalance
```

**Transfer assets from Fund Account to Perpetual Futures:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/api/v3/asset/transfer", {
    type: "FUND_PFUTURES",
    asset: "USDT",
    amount: 100,
  }
);
// result.tranId — transaction ID
```

**Query asset transfer records:**

```typescript
const records = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/api/v3/asset/transfer", {
    type: "FUND_PFUTURES",
    current: 1,
    size: 20,
  }
);
// records.total, records.rows[].asset, records.rows[].amount, records.rows[].status, records.rows[].tranId
```

**Internal P2P transfer to another user (by UID):**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/wallets/v1/capital/innerTransfer/apply", {
    coin: "USDT",
    userAccountType: 1,
    userAccount: "123456789",  // recipient UID
    amount: 50,
    walletType: 1,
  }
);
// result.id — internal transfer record ID
```

**Query internal transfer records:**

```typescript
const records = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/wallets/v1/capital/innerTransfer/records", {
    coin: "USDT",
    limit: 20,
  }
);
// records.data[].id, records.data[].coin, records.data[].amount, records.data[].status, records.data[].receiver
```

## Additional Resources

For full parameter descriptions and response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

Write operations (`POST` asset transfer and internal transfer) require **CONFIRM** on `prod-live`. Read-only queries do not.

- **prod-live**: Ask user to type **CONFIRM** before any asset transfer or internal transfer.
- **prod-vst**: No CONFIRM required. Inform user: "You are operating in the Production Simulated (VST) environment."

### Step 1 — Identify the Operation

If the user's intent is unclear, present options:

> What would you like to do?
> - Check fund account balance
> - View asset overview (all account types)
> - Transfer assets between accounts (e.g., Spot ↔ Futures)
> - View asset transfer history
> - Send an internal transfer to another BingX user
> - View internal transfer history

### Step 2 — Collect details based on operation

**For asset transfer:**
1. Ask for transfer direction:
   > Transfer direction:
   > - Spot → Perpetual Futures (`FUND_PFUTURES`)
   > - Perpetual Futures → Spot (`PFUTURES_FUND`)
   > - Spot → Standard Contract (`FUND_SFUTURES`)
   > - Standard Contract → Spot (`SFUTURES_FUND`)
   > - Standard Contract → Perpetual Futures (`SFUTURES_PFUTURES`)
   > - Perpetual Futures → Standard Contract (`PFUTURES_SFUTURES`)
2. Ask for coin (e.g., `USDT`) and amount.

**For internal transfer:**
1. Ask for coin and amount.
2. Ask for recipient account type:
   > Recipient identifier:
   > - `1` — UID
   > - `2` — Phone number
   > - `3` — Email address
3. Ask for the recipient account value (UID / phone / email).
4. If phone number: ask for calling code (e.g., `86` for China).
5. Ask for source wallet:
   > Source account:
   > - `1` — Fund account
   > - `2` — Standard contract account

### Step 3 — Confirm (prod-live write ops only)

> You are about to transfer **{amount} {coin}** on **Production Live**:
> - Direction: {transfer direction or recipient info}
> - Source: {wallet type}
>
> Type **CONFIRM** to proceed, or anything else to cancel.

### Step 4 — Execute and report

Execute the API call and return key result fields to the user:
- Asset transfer: `tranId`
- Internal transfer: `id` (internal transfer record ID)
- Balance query: list of assets with `free` and `locked` balances
- Asset overview: list of account types with equivalent USDT value
