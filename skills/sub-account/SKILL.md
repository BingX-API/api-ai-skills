---
name: bingx-sub-account
description: BingX sub-account management — create/list sub-accounts, manage API keys, freeze/unfreeze accounts, transfer assets, and query deposit records. Use when the user asks about BingX sub-account creation, sub-account list, sub-account API keys, freeze sub-account, sub-account assets, internal transfers between sub-accounts, or sub-account deposit addresses.
---

# BingX Sub-Account Management

Authenticated endpoints for managing BingX sub-accounts (master account operations). All endpoints require HMAC SHA256 signature authentication. Several write endpoints require `Content-Type: application/json` instead of the standard form encoding — see the **Quick Start** helper below.

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

---

## Quick Reference

| Endpoint | Method | Description | Auth | Body Type |
|----------|--------|-------------|------|-----------|
| `/openApi/account/v1/uid` | GET | Query account UID | Yes | — |
| `/openApi/v1/account/apiPermissions` | GET | Query API Key permissions | Yes | — |
| `/openApi/v1/account/apiPermissions` | GET | Query API Key restrictions | Yes | — |
| `/openApi/account/v1/apiKey/query` | GET | Query API Key info (own or sub-account) | Yes | — |
| `/openApi/subAccount/v1/create` | POST | Create sub-account | Yes | **JSON** |
| `/openApi/subAccount/v1/list` | GET | List sub-accounts | Yes | — |
| `/openApi/subAccount/v1/assets` | GET | Query sub-account fund assets | Yes | — |
| `/openApi/subAccount/v1/updateStatus` | POST | Freeze / unfreeze sub-account | Yes | **JSON** |
| `/openApi/subAccount/v1/allAccountBalance` | GET | Batch query sub-account asset overview | Yes | — |
| `/openApi/subAccount/v1/apiKey/create` | POST | Create API Key for sub-account | Yes | **JSON** |
| `/openApi/subAccount/v1/apiKey/edit` | POST | Edit sub-account API Key | Yes | **JSON** |
| `/openApi/subAccount/v1/apiKey/del` | POST | Delete sub-account API Key | Yes | **JSON** |
| `/openApi/account/v1/innerTransfer/authorizeSubAccount` | POST | Authorize sub-account internal transfers | Yes | form |
| `/openApi/wallets/v1/capital/subAccountInnerTransfer/apply` | POST | Sub-account internal transfer | Yes | form |
| `/openApi/wallets/v1/capital/subAccount/deposit/address` | GET | Get sub-account deposit addresses | Yes | — |
| `/openApi/wallets/v1/capital/deposit/subHisrec` | GET | Get sub-account deposit records | Yes | — |
| `/openApi/wallets/v1/capital/subAccount/innerTransfer/records` | GET | Query sub-account internal transfer records | Yes | — |
| `/openApi/account/transfer/v1/subAccount/asset/transferHistory` | GET | Query sub-account transfer history | Yes | — |
| `/openApi/account/transfer/v1/subAccount/transferAsset/supportCoins` | POST | Query transferable amounts | Yes | form |
| `/openApi/account/transfer/v1/subAccount/transferAsset` | POST | Sub-account asset transfer | Yes | form |
| `/openApi/v1/account/apiRestrictions` | GET | Query API Key permissions for sub-account | Yes | — |
| `/openApi/wallets/v1/capital/deposit/createSubAddress` | POST | Create deposit address for sub-account | Yes | form |

---

## Parameters

### Sub-account Parameters

* **subAccountString**: Sub-account username — must start with a letter, contain a number, and be longer than 6 characters
* **subUid**: Sub-account UID (long integer)
* **note**: Remark/note string for the sub-account or API Key
* **isFeeze**: Boolean — filter sub-accounts by frozen status (note: the API parameter name is `isFeeze`, not `isFreeze`)
* **page**: Page number, starting from 1
* **limit**: Page size, maximum 1000
* **freeze**: Boolean — `true` to freeze, `false` to unfreeze

### API Key Parameters

* **apiKey**: The API Key string of the sub-account
* **uid**: User UID (used when querying API Key info)
* **permissions**: Array of integers — permissions to assign (see Enums)
* **ipAddresses**: Array of IP address strings for the whitelist (optional)

### Transfer Parameters

* **coin**: Currency/asset name (e.g., `USDT`)
* **amount** / **transferAmount**: Transfer amount (float)
* **userAccountType**: `1`=UID, `2`=Phone number, `3`=Email
* **userAccount**: Recipient identifier (UID, phone, or email)
* **walletType** / **fromAccountType** / **toAccountType**: Account type (see Enums)
* **fromUid** / **toUid**: Sender / receiver UID
* **fromType** / **toType**: `1`=Master account, `2`=Sub-account
* **subUids**: Comma-separated UID list string (used for bulk authorization)
* **transferable**: Boolean — `true` to allow, `false` to prohibit internal transfers
* **transferClientId**: Custom client-side transfer ID string

### Enums

**permissions** (API Key permission flags):
- `1` — Spot Trading
- `2` — Read
- `3` — Perpetual Futures Trading
- `4` — Universal Transfer
- `5` — Withdraw
- `7` — Allow internal transfer of sub-accounts

**walletType / accountType** (account type codes):
- `1` — Fund Account
- `2` — Standard Futures Account
- `3` — Perpetual Futures Account (USDⓢ-M)

**status** (deposit record status):
- `0` — In progress
- `1` — Completed
- `6` — Chain uploaded

### Parameter Validation Rules

* **subAccountString**: Must start with a letter, contain at least one number, and be longer than 6 characters
* **subUid**: Positive integer (long)
* **coin**: Uppercase letters and digits only; pattern `^[A-Z0-9]{1,20}$` (e.g., `USDT`)
* **amount** / **transferAmount**: Must be a positive number (> 0)
* **permissions**: Array of integers; each must be one of `1, 2, 3, 4, 5, 7`
* **ipAddresses**: When provided, each must be a valid IPv4 address
* **page**: Positive integer, starting from 1
* **limit**: Positive integer, 1–1000
* **recvWindow**: Integer, 1–5000 ms (see [Replay Protection](../references/authentication.md#replay-protection))
* **timestamp**: Unix time in milliseconds; must be within `recvWindow` of server time

---

## Quick Start

> **Important:** Several sub-account write endpoints require `Content-Type: application/json` with the params sent as a JSON body. Pass `bodyType: "json"` for those calls. All other POST endpoints use the standard form encoding (`bodyType: "form"`).

```typescript
import * as crypto from "crypto";
// Full signing details & edge cases → references/authentication.md
const BASE = {
  "prod-live": ["https://open-api.bingx.com", "https://open-api.bingx.pro"],
  "prod-vst":  ["https://open-api-vst.bingx.com", "https://open-api-vst.bingx.pro"],
};
async function fetchSigned(env: string, apiKey: string, secretKey: string,
  method: "GET" | "POST", path: string, params: Record<string, unknown> = {},
  bodyType: "form" | "json" = "form"
) {
  const urls = BASE[env] ?? BASE["prod-live"];
  const all = { ...params, timestamp: Date.now() };
  const qs = Object.keys(all).sort().map(k => {
    const v = all[k]; return `${k}=${Array.isArray(v) ? JSON.stringify(v) : v}`;
  }).join("&");
  const sig = crypto.createHmac("sha256", secretKey).update(qs).digest("hex");
  for (const base of urls) {
    try {
      if (method === "GET") {
        const r = await fetch(`${base}${path}?${qs}&signature=${sig}`,
          { headers: { "X-BX-APIKEY": apiKey, "X-SOURCE-KEY": "BX-AI-SKILL" } });
        const j = await r.json(); if (j.code !== 0) throw new Error(`BingX error ${j.code}: ${j.msg}`);
        return j.data;
      }
      const ct = bodyType === "json" ? "application/json" : "application/x-www-form-urlencoded";
      const body = bodyType === "json" ? JSON.stringify({ ...all, signature: sig }) : `${qs}&signature=${sig}`;
      const r = await fetch(`${base}${path}`, { method: "POST",
        headers: { "X-BX-APIKEY": apiKey, "X-SOURCE-KEY": "BX-AI-SKILL", "Content-Type": ct }, body });
      const j = await r.json(); if (j.code !== 0) throw new Error(`BingX error ${j.code}: ${j.msg}`);
      return j.data;
    } catch (e) {
      if (base === urls[urls.length - 1]) throw e;
    }
  }
}
```

---

## Common Calls

**Query account UID:**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/account/v1/uid"
);
// data.uid
```

**Create a sub-account:**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/subAccount/v1/create",
  { subAccountString: "alice001", note: "trading sub" },
  "json"  // must use JSON body
);
// data.subUid, data.subAccountString
```

**List sub-accounts (paginated):**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/subAccount/v1/list",
  { page: 1, limit: 100 }
);
// data.subAccountList[].uid, .subAccountString, .isFreeze
```

**Create API Key for a sub-account:**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/subAccount/v1/apiKey/create",
  {
    subUid: 16477999,
    note: "read-only key",
    permissions: [2],           // 2 = Read only
    ipAddresses: ["1.2.3.4"],
  },
  "json"  // must use JSON body
);
// data.apiKey, data.secretKey
```

**Freeze a sub-account:**

```typescript
await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/subAccount/v1/updateStatus",
  { subUid: 16477999, freeze: true },
  "json"  // must use JSON body
);
```

**Transfer assets between sub-accounts (master only):**

```typescript
const data = await fetchSigned("prod-live", API_KEY, SECRET, "POST",
  "/openApi/account/transfer/v1/subAccount/transferAsset",
  {
    assetName: "USDT",
    transferAmount: 100,
    fromUid: 11111111,
    fromType: 1,           // 1 = master account
    fromAccountType: 1,    // 1 = fund account
    toUid: 22222222,
    toType: 2,             // 2 = sub-account
    toAccountType: 1,
    remark: "funding sub",
  }
  // default form body
);
// data.tranId
```

## Additional Resources

For full parameter descriptions and response schemas for all 21 endpoints, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

All write operations require **CONFIRM** on `prod-live`. Read-only queries do not.

- **prod-live**: Ask user to type **CONFIRM** before any create, edit, delete, freeze, or transfer operation.
- **prod-vst**: No CONFIRM required. Inform user: "You are operating in the Production Simulated (VST) environment."

### Step 1 — Identify the Operation

If the user's intent is unclear, present options:

> What would you like to do?
> - Query account UID or API Key permissions
> - Create a new sub-account
> - List sub-accounts
> - Query sub-account assets / asset overview
> - Freeze or unfreeze a sub-account
> - Create / edit / delete a sub-account API Key
> - Query a sub-account's API Keys
> - Authorize sub-account internal transfers
> - Transfer assets between accounts
> - Query deposit address or deposit records
> - Query transfer history

### Step 2 — Collect sub-account identifier (if applicable)

> Please provide the sub-account UID, or sub-account username if creating a new one.

### Step 3 — Collect operation-specific parameters

**Create sub-account:** Ask for `subAccountString` (must start with letter, contain number, >6 chars). Ask for optional `note`.

**Create / Edit API Key:** Ask for:
- `subUid` (sub-account UID)
- `note` (label)
- `permissions` (present the list: 1=Spot, 2=Read, 3=Perp Futures, 4=Universal Transfer, 5=Withdraw, 7=Internal Transfer)
- `ipAddresses` (optional IP whitelist)

**Freeze / Unfreeze:** Ask whether to freeze (`true`) or unfreeze (`false`).

**Asset Transfer:** Ask for:
- `assetName` (e.g., USDT)
- `transferAmount`
- sender UID + account type
- receiver UID + account type

### Step 4 — Confirm (prod-live write ops only)

> You are about to **{action}** on **Production Live**:
> - {Summary of parameters}
>
> Type **CONFIRM** to proceed, or anything else to cancel.

### Step 5 — Execute and report

Execute the API call using the helper function (use `bodyType: "json"` for `create`, `updateStatus`, `apiKey/create`, `apiKey/edit`, `apiKey/del`; use default `"form"` for all other POST endpoints).

Return key fields to the user (e.g., `subUid`, `apiKey`, `tranId`).

---

### JSON Body Endpoints (Reminder)

Always pass `bodyType: "json"` for these paths:
- `POST /openApi/subAccount/v1/create`
- `POST /openApi/subAccount/v1/updateStatus`
- `POST /openApi/subAccount/v1/apiKey/create`
- `POST /openApi/subAccount/v1/apiKey/edit`
- `POST /openApi/subAccount/v1/apiKey/del`

All other POST endpoints use the default form encoding.
