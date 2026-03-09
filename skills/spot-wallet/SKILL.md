---
name: bingx-spot-wallet
description: BingX wallet deposits and withdrawals — query deposit/withdrawal history, get coin network config, initiate withdrawals, and fetch deposit addresses. Use when the user asks about BingX deposit records, withdrawal records, coin network fees, withdrawal limits, deposit addresses, or initiating a withdrawal.
---

# BingX Spot Wallet

Authenticated endpoints for BingX wallet deposits and withdrawals. All endpoints require HMAC SHA256 signature authentication.

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

---

## Quick Reference

| Endpoint | Method | Description | Auth | Permission |
|----------|--------|-------------|------|------------|
| `/openApi/api/v3/capital/deposit/hisrec` | GET | Query deposit history | Yes | Read |
| `/openApi/api/v3/capital/withdraw/history` | GET | Query withdrawal history | Yes | Read |
| `/openApi/wallets/v1/capital/config/getall` | GET | Query coin deposit/withdrawal config (networks, limits, fees) | Yes | Read |
| `/openApi/wallets/v1/capital/withdraw/apply` | POST | Initiate a withdrawal | Yes | Withdraw |
| `/openApi/wallets/v1/capital/deposit/address` | GET | Query main account deposit address | Yes | Read |
| `/openApi/wallets/v1/capital/deposit/riskRecords` | GET | Query deposit risk control records | Yes | Read |

---

## Parameters

### Deposit History Parameters

* **coin**: Coin name (e.g., `USDT`, `BTC`); optional — returns all coins if omitted
* **status**: Filter by deposit status (see DepositStatus enum)
* **startTime**: Start of time range in milliseconds (e.g., `1658748648396`)
* **endTime**: End of time range in milliseconds
* **offset**: Pagination offset, default `0`
* **limit**: Page size, default `1000`; max `1000`
* **txId**: Filter by blockchain transaction ID
* **recvWindow**: Request validity window in milliseconds (max `60000`)

### Withdrawal History Parameters

* **id**: Unique withdrawal record ID
* **coin**: Coin name; optional
* **withdrawOrderId**: Custom withdrawal ID assigned at submission
* **status**: Filter by withdrawal status (see WithdrawalStatus enum)
* **startTime** / **endTime**: Time range in milliseconds
* **offset**: Pagination offset, default `0`
* **limit**: Page size, default `1000`
* **txId**: Filter by blockchain transaction ID

### Withdrawal Apply Parameters

* **coin**: Coin name (required, e.g., `USDT`)
* **network**: Network name (e.g., `BEP20`, `ERC20`); uses default if omitted
* **address**: Withdrawal destination address (required)
* **addressTag**: Memo or tag for coins that require it (e.g., XRP, EOS)
* **amount**: Withdrawal amount (required)
* **walletType**: Source account type (required; see WalletType enum)
* **withdrawOrderId**: Custom withdrawal ID (optional, for idempotency)
* **vaspEntityId**: Payment platform info (optional, for Travel Rule compliance)
* **recipientLastName** / **recipientFirstName**: Recipient name in English (optional, Travel Rule)
* **dateOfbirth**: Recipient date of birth, format `YYYY-MM-DD` (optional, Travel Rule)

### Deposit Address Parameters

* **coin**: Coin name (required)
* **offset**: Starting record number, default `0`
* **limit**: Page size, default `100`; max `1000`

### Enums

**DepositStatus** (deposit record status):
- `0` — In progress
- `1` — Not credited
- `2` — Wrong amount
- `6` — Chain confirmed / completed

**WithdrawalStatus** (withdrawal record status):
- `4` — Under review
- `5` — Failed
- `6` — Completed

**WalletType** (source account for withdrawal):
- `1` — Fund account (spot)
- `2` — Standard contract account
- `3` — Perpetual futures account

### Parameter Validation Rules

Before sending a request, validate parameters client-side to avoid unnecessary API errors:

* **coin**: Uppercase letters and digits only; pattern `^[A-Z0-9]{1,20}$` (e.g., `USDT`, `BTC`)
* **address**: Non-empty string; max 200 characters; must be a valid blockchain address for the target network
* **amount**: Must be a positive number (> 0); must meet the minimum withdrawal amount for the coin/network (query via coin network config endpoint)
* **network**: Uppercase network identifier (e.g., `ERC20`, `BEP20`, `TRC20`); must match a supported network for the coin
* **addressTag**: When required by the coin (e.g., XRP, EOS), must be a non-empty string; max 128 characters
* **limit**: Integer, 1–1000; default is `1000` for history, `100` for addresses
* **startTime** / **endTime**: Unix timestamps in milliseconds; `endTime` must be ≥ `startTime`; max range 90 days
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

**Query deposit history (last 7 days, USDT):**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/api/v3/capital/deposit/hisrec", {
    coin: "USDT",
    startTime: Date.now() - 7 * 24 * 60 * 60 * 1000,
    endTime: Date.now(),
    limit: 100,
  }
);
// data[].amount, data[].coin, data[].status, data[].txId, data[].insertTime
```

**Query withdrawal history:**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/api/v3/capital/withdraw/history", {
    coin: "USDT",
    limit: 50,
  }
);
// data[].id, data[].amount, data[].coin, data[].status, data[].address, data[].txId
```

**Query supported networks and fees for a coin:**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/wallets/v1/capital/config/getall", {
    coin: "USDT",
  }
);
// data[].coin, data[].networkList[].network, data[].networkList[].withdrawFee
// data[].networkList[].withdrawMin, data[].networkList[].depositEnable
```

**Get deposit address for USDT:**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/wallets/v1/capital/deposit/address", {
    coin: "USDT",
    limit: 10,
  }
);
// data.data[].address, data.data[].coin, data.data[].network, data.data[].tag
```

**Initiate a withdrawal:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/wallets/v1/capital/withdraw/apply", {
    coin: "USDT",
    network: "BEP20",
    address: "0xYourAddress",
    amount: 100,
    walletType: 1,
  }
);
// result.id — the unique withdrawal record ID
```

## Additional Resources

For full parameter descriptions and response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

The withdrawal endpoint (`POST /openApi/wallets/v1/capital/withdraw/apply`) is a write operation requiring **CONFIRM** on `prod-live`. All other endpoints are read-only.

- **prod-live**: Ask user to type **CONFIRM** before initiating any withdrawal.
- **prod-vst**: No CONFIRM required. Inform user: "You are operating in the Production Simulated (VST) environment."

### Step 1 — Identify the Operation

If the user's intent is unclear, present options:

> What would you like to do?
> - View deposit history
> - View withdrawal history
> - Check coin network info (fees, limits, enabled networks)
> - Get deposit address for a coin
> - Initiate a withdrawal
> - View deposit risk control records

### Step 2 — Collect coin (if applicable)

> Please enter the coin name (e.g., USDT, BTC, ETH):

### Step 3 — Collect time range (for history queries, optional)

> Optionally provide a time range:
> - Last 24 hours
> - Last 7 days
> - Last 30 days
> - Custom range (provide startTime and endTime in milliseconds)

### Step 4 — Collect withdrawal details (for withdrawal only)

1. Ask for **coin** (e.g., `USDT`)
2. Ask for **network** (e.g., `BEP20`, `ERC20`, `TRC20`). Suggest fetching `/capital/config/getall` first to see available networks and fees.
3. Ask for **address** (destination wallet address)
4. Ask for **addressTag** if the coin requires a memo/tag (e.g., XRP, EOS, XLM)
5. Ask for **amount**
6. Ask for **walletType** (source account):
   > Source account:
   > - 1 — Fund account (spot)
   > - 2 — Standard contract
   > - 3 — Perpetual futures

### Step 5 — Confirm (prod-live withdrawal only)

> You are about to initiate the following withdrawal on **Production Live**:
> - Coin: USDT
> - Network: BEP20
> - Address: 0x...
> - Amount: 100
> - Source: Fund account (walletType=1)
>
> Type **CONFIRM** to proceed, or anything else to cancel.

### Step 6 — Execute and report

Execute the API call and return the key result fields to the user:
- Deposit/withdrawal history: record count, statuses, amounts, txIds
- Coin config: available networks, fees, min/max limits
- Deposit address: address string and network
- Withdrawal: the returned `id` (unique withdrawal record ID)
