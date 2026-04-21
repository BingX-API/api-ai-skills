# BingX Announcement — API Reference

**Base URLs:** see [`references/base-urls.md`](../references/base-urls.md) | **Auth:** None (public endpoint) | **Response:** `{ "code": 0, "msg": "", "data": ... }`

---

## 1. Get Announcements

`GET /openApi/content/v1/announcement`

Rate limit: see [`references/rate-limits.md`](../references/rate-limits.md) for global policy (per-UID + per-IP throttling, 100410 backoff).

Returns announcements filtered by module type, with pagination support.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `contentType` | string | No | Module type: `LatestAnnouncements`, `LatestPromotions`, `ProductUpdates`, `AssetMaintenance`, `SystemMaintenance`, `SpotListing`, `FuturesListing`, `InnovationListing`, `FundingRate`, `Delisting`, `CryptoScout`. Omit for default. |
| `language` | string | No | Language: `zh-tw` (Traditional Chinese), `en-us` (English). |
| `page` | integer | No | Page number for pagination; minimum `1`. |

### contentType Enum

| Value | Description |
|-------|-------------|
| `LatestAnnouncements` | Latest announcements |
| `LatestPromotions` | Latest promotions |
| `ProductUpdates` | Product updates |
| `AssetMaintenance` | Asset maintenance |
| `SystemMaintenance` | System maintenance |
| `SpotListing` | Spot new listings |
| `FuturesListing` | Futures new listings |
| `InnovationListing` | Innovation zone new listings |
| `FundingRate` | Funding rate |
| `Delisting` | Delisting notices |
| `CryptoScout` | Crypto scout |

**Response `data`:**

| Field | Type | Description |
|-------|------|-------------|
| `list` | array | Array of announcement objects |
| `list[].title` | string | Announcement title |
| `list[].time` | string | Publication time |
| `list[].link` | string | Full announcement URL |
| `list[].content` | string | Announcement content or summary |
| `list[].type` | string | Announcement type identifier |
| `total` | integer | Total number of announcements matching the filter |
| `page` | integer | Current page number |

**Example Response:**

```json
{
  "code": 0,
  "msg": "",
  "data": {
    "list": [
      {
        "title": "BingX Will List TOKEN (TOKEN) in the Innovation Zone",
        "time": "2026-03-15 12:00:00",
        "link": "https://bingx.com/en/support/announcement/detail/12345",
        "content": "BingX is excited to announce that TOKEN will be listed...",
        "type": "SpotListing"
      }
    ],
    "total": 58,
    "page": 1
  }
}
```

---

## Error Handling

Standard BingX error format: `{ "code": <non-zero>, "msg": "<description>" }`.

If `code !== 0`, treat as error and surface `msg`. On network/timeout, retry with the fallback base URL.

Common gateway error codes applicable to all endpoints:

| Code | Description |
|------|-------------|
| `100001` | Request signature verification failed. Verify the signature algorithm, parameter order, and API secret. |
| `100004` | The API key does not have the required trading permission. Enable it in the API Key management page. |
| `100410` | Request rate limit exceeded. Reduce request frequency and retry after the cooldown period. |
| `100412` | Request is missing the signature parameter. Include a valid signature in your request. |
| `100413` | API Key is incorrect or missing. Ensure `X-BX-APIKEY` is set in the HTTP request header. |
| `100419` | The request IP is not in the API Key IP whitelist. Check IP whitelist settings. |
| `100421` | Null timestamp or timestamp mismatch with server time. Ensure your local clock is synchronized. |
| `100500` | System busy. Please retry later. |

For the complete error code list, see [Error Code Reference](../references/error-codes.md).
