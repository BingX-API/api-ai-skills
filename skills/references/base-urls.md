# Base URLs

All BingX OpenAPI endpoints share the same base URL prefix. Choose the environment that matches your use case.

## Environment Table

| Environment ID | Description | Base URL (Primary) | Base URL (Fallback) |
|----------------|-------------|---------------------|---------------------|
| `prod-live` | Production Live | `https://open-api.bingx.com` | `https://open-api.bingx.pro` |
| `prod-vst` | Production Simulated (Testnet) | `https://open-api-vst.bingx.com` | `https://open-api-vst.bingx.pro` |

Select `prod-live` for real trading or `prod-vst` for simulation explicitly. Missing or unknown environments must fail before any request. Keep authenticated destinations fixed to the official URLs in this table and disable HTTP redirects.

## Domain Priority Constraint

**The `.com` domain is the mandatory primary endpoint. The `.pro` domain is a fallback ONLY for network-level failures.**

1. **Always call `.com` first** — every request must target the primary `.com` domain.
2. **Fallback for GET only** — a read-only GET may use `.pro` after a network error or timeout. Writes must use the primary once. On a timeout, interrupted response, invalid response or HTTP error for a write, report `OUTCOME_UNKNOWN` and reconcile the operation status before considering a new write. A lost response does not prove the operation failed.
3. **Never fallback on business errors** — if the `.com` domain responds with an HTTP status and a valid JSON body (even if `code !== 0`), that is a successful network round-trip. Do **not** retry with `.pro`; throw the business error immediately.

## TypeScript Helper

Use this constant in your code to switch environments easily. Each environment maps to an array of URLs — primary first, fallback second:

```typescript
const BASE_URLS: Record<string, string[]> = {
  "prod-live": ["https://open-api.bingx.com", "https://open-api.bingx.pro"],
  "prod-vst":  ["https://open-api-vst.bingx.com", "https://open-api-vst.bingx.pro"],
};

function getBaseUrls(env: string): string[] {
  if (env !== "prod-live" && env !== "prod-vst") throw new Error("UnknownEnvironment");
  return BASE_URLS[env];
}

function isNetworkOrTimeout(e: unknown): boolean {
  if (e instanceof TypeError) return true;
  if (e instanceof DOMException && e.name === "AbortError") return true;
  if (e instanceof Error && e.name === "TimeoutError") return true;
  return false;
}
```
