# BingX API Authentication

## Generate an API Key

To access private endpoints, create an API Key at [User Center → API Management](https://bingx.com/en/accounts/api).

After creation you will receive an **API Key** and a **Secret Key**. Keep them secure.

- It is strongly recommended to configure an **IP whitelist** for each key.
- Never disclose your API Key or Secret Key. If leaked, delete it immediately and create a new one.

---

## Permission Settings

Newly created API Keys have **read-only** permission by default.

To place orders or perform other write operations, enable the corresponding permissions in the API Management UI.

---

## Base URLs

See [`base-urls.md`](base-urls.md) for the full environment table and TypeScript helper.

---

## Overview

All authenticated endpoints require:

1. `X-BX-APIKEY` request header with your API key
2. `signature` query parameter (HMAC SHA256 of the canonical parameter string)
3. `timestamp` parameter (Unix time in **milliseconds**)

---

## Signing Process

### Step 1 — Build the Parameter String

Collect **all** request parameters (query string + request body fields), **sort them in ASCII ascending order by key name**, then join as `key=value&key=value`.

- Do **not** URL-encode parameter values before signing.
- Do **not** include `signature` itself.

**Example parameters (after ASCII sort):**

```
limit=100&recvWindow=5000&symbol=BTC-USDT&timestamp=170273150000&type=MARKET
```

### Step 2 — Sign with HMAC SHA256

```
signature = HMAC_SHA256(secretKey, parameterString)
```

Encode the result as a lowercase hex string.

### Step 3 — Append Signature

Append `&signature=<hex>` to the request URL's query string.

### Step 4 — Set Header

Add `X-BX-APIKEY: <apiKey>` to the HTTP request headers.

---

## URL Encoding Rules

These rules apply to **query string parameters only** (not the signing string):

- The signature is always computed from the **unencoded** signing string.
- If the signing string contains `[` or `{`, URL-encode only the **parameter values** in the actual request URL. Do **not** encode parameter keys.
- Use UTF-8 encoding; encode spaces as `%20`.
- If the signing string does **not** contain `[` or `{`, values do not need URL encoding.

---

## Examples

### Query String Example

**Parameters:**

| Key | Value |
|-----|-------|
| symbol | BTC-USDT |
| recvWindow | 0 |
| timestamp | 1696751141337 |

**Sorted signing string** (ASCII order, no URL encoding):

```
recvWindow=0&symbol=BTC-USDT&timestamp=1696751141337
```

**Generate signature** (shell):

```bash
echo -n 'recvWindow=0&symbol=BTC-USDT&timestamp=1696751141337' | openssl dgst -sha256 -hmac 'SECRET_KEY' -hex
```

**Final request URL:**

```
https://open-api.bingx.com/xxx?recvWindow=0&symbol=BTC-USDT&timestamp=1696751141337&signature=<hex>
```

---

### Batch Order Query String Example

When a parameter value contains `[` or `{`, URL-encode only the **value** (not the key) in the request URL. The signing string still uses the raw unencoded value.

**Example URL** (the `data` value is URL-encoded):

```
https://open-api.bingx.com/openApi/spot/v1/trade/batchOrders?data=%5B%7B%22symbol%22%3A%22BTC-USDT%22%2C%22side%22%3A%22BUY%22%2C%22type%22%3A%22LIMIT%22%2C%22quantity%22%3A0.001%2C%22price%22%3A85000%7D%5D&recvWindow=5000&timestamp=1766679008165&signature=<hex>
```

---

### JSON Request Body Example

For endpoints that use `application/json`, `timestamp` and `signature` must be included **inside the request body** — do not append them to the URL query string.

**Business parameters:**

```json
{
  "recvWindow": 5000,
  "symbol": "ETH-USDT",
  "type": "MARKET",
  "side": "SELL",
  "positionSide": "SHORT",
  "quantity": 0.01
}
```

**Signing string** (all fields including timestamp, ASCII-sorted):

```
positionSide=SHORT&quantity=0.01&recvWindow=5000&side=SELL&symbol=ETH-USDT&timestamp=1696751141337&type=MARKET
```

**Final request body:**

```json
{
  "recvWindow": 5000,
  "symbol": "ETH-USDT",
  "type": "MARKET",
  "side": "SELL",
  "positionSide": "SHORT",
  "quantity": 0.01,
  "timestamp": 1696751141337,
  "signature": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

---

## Timestamp & recvWindow

- `timestamp`: current Unix time in milliseconds.
- `recvWindow` (optional): specifies how many milliseconds the request is valid. Default is `5000`; maximum is `5000`.
- The server rejects requests where `serverTime - timestamp > recvWindow`.

---

## Replay Protection

BingX API uses `timestamp` + `recvWindow` to guard against replay attacks. The server rejects any request whose timestamp falls outside the acceptance window. To maximize security:

- **Keep recvWindow as small as possible.** The default of `5000` (5 seconds) is recommended. Only increase it if you experience clock-drift or high-latency conditions.
- **Synchronize your clock.** Use NTP or the BingX server-time endpoint (`GET /openApi/swap/v1/server/time`) to keep your local clock within 1–2 seconds of the server.
- **Use HTTPS only.** All BingX API base URLs enforce TLS. Never downgrade to HTTP — this prevents man-in-the-middle interception and replay.
- **Nonce (not yet supported).** The BingX API does not currently accept a `nonce` parameter. If nonce support is added in the future, include a `crypto.randomUUID()` value in every request for stronger per-request uniqueness. Monitor the official changelog for updates.
- **IP whitelist.** Binding your API Key to a specific IP address prevents replayed requests from unauthorized networks, even within the `recvWindow` window.

---

## TypeScript Helper

```typescript
import * as crypto from "crypto";

// Base URLs — see references/base-urls.md for all environments
// Each env maps to [primary, fallback]; fallback is used when primary is unreachable.
const ENV_URLS: Record<string, string[]> = {
  "prod-live": ["https://open-api.bingx.com", "https://open-api.bingx.pro"],
  "prod-vst":  ["https://open-api-vst.bingx.com", "https://open-api-vst.bingx.pro"],
};

/**
 * Build the canonical signing string: ASCII-sort all keys, join as key=value pairs.
 * Values must NOT be URL-encoded at this stage.
 */
function buildCanonical(params: Record<string, unknown>): string {
  return Object.keys(params)
    .sort()
    .map((k) => `${k}=${params[k]}`)
    .join("&");
}

/**
 * URL-encode only the values in a query string when the canonical string
 * contains '[' or '{' (e.g. batch order arrays). Keys are never encoded.
 */
function encodeQueryValues(params: Record<string, unknown>, signature: string): string {
  const pairs = Object.keys(params)
    .sort()
    .map((k) => {
      const v = String(params[k]);
      const needsEncoding = v.includes("[") || v.includes("{");
      return `${k}=${needsEncoding ? encodeURIComponent(v) : v}`;
    });
  pairs.push(`signature=${signature}`);
  return pairs.join("&");
}

/**
 * Make a signed BingX REST request.
 *
 * @param jsonBody - When true, sends POST body as application/json with
 *                   timestamp and signature embedded in the JSON object.
 *                   When false (default), uses application/x-www-form-urlencoded.
 */
async function fetchSigned(
  env: string,
  apiKey: string,
  secretKey: string,
  method: "GET" | "POST" | "DELETE",
  path: string,
  params: Record<string, unknown> = {},
  jsonBody = false
): Promise<unknown> {
  const baseUrls = ENV_URLS[env] ?? ENV_URLS["prod-live"];
  const timestamp = Date.now();
  const allParams = { ...params, timestamp };

  const canonical = buildCanonical(allParams);

  const signature = crypto
    .createHmac("sha256", secretKey)
    .update(canonical)
    .digest("hex");

  const needsValueEncoding = canonical.includes("[") || canonical.includes("{");

  for (const baseUrl of baseUrls) {
    try {
      let url: string;
      let body: string | undefined;
      let contentType: string | undefined;

      if (method === "POST" && jsonBody) {
        url = `${baseUrl}${path}`;
        body = JSON.stringify({ ...allParams, signature });
        contentType = "application/json";
      } else if (method === "POST") {
        url = `${baseUrl}${path}`;
        body = `${canonical}&signature=${signature}`;
        contentType = "application/x-www-form-urlencoded";
      } else {
        const query = needsValueEncoding
          ? encodeQueryValues(allParams, signature)
          : `${canonical}&signature=${signature}`;
        url = `${baseUrl}${path}?${query}`;
      }

      const res = await fetch(url, {
        method,
        headers: {
          "X-BX-APIKEY": apiKey,
          "X-SOURCE-KEY": "BX-AI-SKILL",
          ...(contentType ? { "Content-Type": contentType } : {}),
        },
        body,
      });

      const json = await res.json();
      if (json.code !== 0) throw new Error(`BingX error ${json.code}: ${json.msg}`);
      return json.data;
    } catch (e) {
      if (baseUrl === baseUrls[baseUrls.length - 1]) throw e;
    }
  }
}
```

---

## Example: Place an Order (POST)

```typescript
const result = await fetchSigned(
  "prod-live",
  "YOUR_API_KEY",
  "YOUR_SECRET_KEY",
  "POST",
  "/openApi/swap/v2/trade/order",
  {
    symbol: "BTC-USDT",
    side: "BUY",
    positionSide: "LONG",
    type: "MARKET",
    quantity: 0.01,
    recvWindow: 5000,
  }
);
```

## Example: Query Open Orders (GET)

```typescript
const orders = await fetchSigned(
  "prod-live",
  "YOUR_API_KEY",
  "YOUR_SECRET_KEY",
  "GET",
  "/openApi/swap/v2/trade/openOrders",
  { symbol: "BTC-USDT" }
);
```

## Example: Place an Order (POST, JSON body)

For endpoints that accept `application/json`, pass `jsonBody: true`. The helper will embed `timestamp` and `signature` in the JSON object.

```typescript
const result = await fetchSigned(
  "prod-live",
  "YOUR_API_KEY",
  "YOUR_SECRET_KEY",
  "POST",
  "/openApi/swap/v2/trade/order",
  {
    symbol: "ETH-USDT",
    type: "MARKET",
    side: "SELL",
    positionSide: "SHORT",
    quantity: 0.01,
    recvWindow: 5000,
  },
  true // jsonBody
);
```

---

## Success Response

An HTTP `200` status code indicates a successful response. The response body is JSON:

```json
{
  "code": 0,
  "msg": "",
  "data": { ... }
}
```

A `code` of `0` means success. Any non-zero `code` indicates an error — the `msg` field contains the error description.
