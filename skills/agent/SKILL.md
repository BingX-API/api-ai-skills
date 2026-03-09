---
name: bingx-agent
description: BingX Agent (affiliate/broker) management — query invited users, daily commission details, agent user information, API transaction commission, and partner information. Use when the user asks about BingX agent invited users, affiliate commissions, referral relationships, partner data, or broker commission reports.
---

# BingX Agent

Authenticated read-only endpoints for BingX Agent (affiliate/broker) data. All endpoints require HMAC SHA256 signature authentication.

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Authentication:** see [`references/authentication.md`](../references/authentication.md)

---

## Quick Reference

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/openApi/agent/v1/account/inviteAccountList` | GET | Query invited users (paginated) | Yes |
| `/openApi/agent/v2/reward/commissionDataList` | GET | Daily commission details (invitation relationship) | Yes |
| `/openApi/agent/v1/account/inviteRelationCheck` | GET | Query agent user information for a UID | Yes |
| `/openApi/agent/v1/reward/third/commissionDataList` | GET | API transaction commission (non-invitation relationship) | Yes |
| `/openApi/agent/v1/asset/partnerData` | GET | Query partner information | Yes |
| `/openApi/agent/v1/asset/depositDetailList` | GET | Query deposit details of invited users | Yes |
| `/openApi/agent/v1/commissionDataList/referralCode` | GET | Query invitation code commission data | Yes |
| `/openApi/agent/v1/account/superiorCheck` | GET | Check if a user is a superior agent | Yes |

---

## Parameters

### Pagination Parameters

* **pageIndex**: Page number — must be greater than 0
* **pageSize**: Page size — must be greater than 0; maximum value varies by endpoint (100 or 200)

### Invited Users Parameters

* **startTime**: Start timestamp in **milliseconds**; maximum query window is 30 days; omit for all-time query
* **endTime**: End timestamp in **milliseconds**; maximum query window is 30 days; omit for all-time query
* **lastUid**: Required when queried data exceeds 10,000 records — pass the last UID of the current page on each subsequent request
* **recvWindow**: Request validity window in milliseconds (default 5 seconds)

### Commission Parameters

* **startTime**: Start timestamp in **days** (date string, e.g. `"20240101"`); maximum query window 30 days; sliding range of last 365 days
* **endTime**: End timestamp in **days** (date string); maximum query window 30 days
* **uid**: Optional — filter by a specific invited user UID
* **recvWindow**: Request validity window in milliseconds

### API Commission (Non-Invitation) Parameters

* **commissionBizType**: `81` = Perpetual contract API commission; `82` = Spot trading API commission
* **startTime**: Start timestamp in **days**; supports data after December 1, 2023
* **endTime**: End timestamp in **days**; supports data after December 1, 2023
* **uid**: Optional — UID of the trading user (non-invitation relationship)

### Partner Information Parameters

* **startTime**: Start timestamp in **days**; supports last 3 months only
* **endTime**: End timestamp in **days**; supports last 3 months only
* **uid**: Optional — filter by a specific partner UID
* **pageSize**: Maximum value 200 for this endpoint

### Enums

**commissionBizType**:
- `81` — Perpetual contract API commission
- `82` — Spot trading API commission

### Parameter Validation Rules

* **pageIndex**: Positive integer, must be > 0
* **pageSize**: Positive integer, must be > 0; max 100 or 200 depending on endpoint
* **startTime** / **endTime**: Format varies — milliseconds for invited users, date string `"YYYYMMDD"` for commission/partner endpoints; `endTime` must be ≥ `startTime`; max query window 30 days
* **uid**: When provided, must be a positive integer
* **commissionBizType**: Must be `81` (perpetual) or `82` (spot)
* **lastUid**: When paginating > 10,000 records, pass the last UID from the previous page
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

**Query all invited users (first page):**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/agent/v1/account/inviteAccountList", {
    pageIndex: 1,
    pageSize: 100,
  }
);
// result.list — array of invited users
// result.total — total count
// result.currentAgentUid — current agent UID
```

**Query invited users with time filter:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/agent/v1/account/inviteAccountList", {
    pageIndex: 1,
    pageSize: 100,
    startTime: 1704067200000,  // milliseconds
    endTime:   1706745600000,
  }
);
```

**Query daily commissions for a date range:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/agent/v2/reward/commissionDataList", {
    startTime: "20240101",
    endTime:   "20240131",
    pageIndex: 1,
    pageSize:  100,
  }
);
// result.list — array of CommissionData per user per day
// result.total — total records
```

**Query agent user information for a specific UID:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/agent/v1/account/inviteRelationCheck", {
    uid: 123456789,
  }
);
// result.uid, result.inviteResult, result.deposit, result.trade, etc.
```

**Query API transaction commission (non-invitation, perpetual):**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/agent/v1/reward/third/commissionDataList", {
    commissionBizType: 81,   // 81=perpetual, 82=spot
    startTime: "20240101",
    endTime:   "20240131",
    pageIndex: 1,
    pageSize:  100,
  }
);
```

**Query partner information:**

```typescript
const result = await fetchSigned("prod-live", API_KEY, SECRET, "GET",
  "/openApi/agent/v1/asset/partnerData", {
    startTime: 20240101,   // days
    endTime:   20240131,
    pageIndex: 1,
    pageSize:  200,
  }
);
```

## Additional Resources

For full parameter descriptions and response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

All Agent endpoints are **read-only** (GET). No `CONFIRM` is required in any environment.

- **prod-live**: No CONFIRM needed (read-only). Proceed directly.
- **prod-vst**: No CONFIRM required. Inform user: "You are operating in the Production Simulated (VST) environment."

### Step 1 — Identify the Operation

If the user's intent is unclear, present options:

> What would you like to do?
> - Query my invited/referred users list
> - Query daily commission details (invitation relationship)
> - Look up agent relationship info for a specific user UID
> - Query API transaction commission (non-invitation relationship)
> - Query partner information

### Step 2 — Collect Time Range (if applicable)

For commission and partner endpoints:

> Please specify a date range (max 30 days window):
> - Start date (e.g., 20240101)
> - End date (e.g., 20240131)

For invited users list, timestamps are in milliseconds:

> Please specify a time range (optional, max 30-day window):
> - Start time (Unix ms) or leave blank for all-time

### Step 3 — Collect Optional Filters

- For commission queries: optionally filter by a specific **invited user UID**
- For API commission queries: ask for **commissionBizType** (81=perpetual, 82=spot)
- For large datasets (>10,000 records): use **lastUid** cursor for pagination

### Step 4 — Execute and Report

Execute the API call and return key fields to the user:
- For invited users: total count, current page, and a summary of user details
- For commission data: total records, current agent UID, and aggregated commission amounts
- For user info: invitation relationship, KYC status, deposit/trade status, and welfare info
