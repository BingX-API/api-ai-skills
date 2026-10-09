# BingX API Rate Limits

## Source Fields and IP Groups

The API documentation field `api.rate-limitation` specifies the documented UID request rate. The field `api.ip-rate-limitation` is an IP policy group identifier, not a requests-per-second value. Never append a requests-per-second unit to a group identifier.

The documentation changelog dated 2025-12-16 states that the former IP limits for account endpoint groups 2 and 3 were removed: the group-wide 2000 requests per 10 seconds and per-endpoint 300 requests per 10 seconds no longer apply.

Group 1 is displayed as 500 requests per 10 seconds in the documentation renderer, not 1 request per second. Existing group-1 annotations require a separate endpoint-by-endpoint audit; do not infer a live gateway limit from an identifier.

Removal of the former group limits does not imply unlimited requests, exemption from other service protections, or verification of the live gateway configuration for every source IP.

## Endpoint Annotations

For `GET /openApi/swap/v2/trade/openOrders`:

```text
Rate limit: 5/s per UID.
```

The source IP group is 3. The former group-specific IP limits were removed as described above. A UID-only annotation does not assert that no other IP protection exists.

Other account endpoint annotations retain their existing UID rates while removing unsupported IP rates derived from groups 2 and 3. This correction does not independently revalidate every UID rate.

The following method/path pairs could not be matched exactly to the checked documentation source. Their current endpoint availability and limits still require verification; removed IP values must not be interpreted as an exemption:

- `GET /openApi/copyTrading/v1/swap/trace/currentTrack`
- `POST /openApi/copyTrading/v1/swap/trace/closeTrackOrder`
- `POST /openApi/cswap/v1/trade/order`
- `POST /openApi/cswap/v1/trade/allOpenOrders`
- `GET /openApi/swap/v1/trade/positionHistory`

Where no documented UID rate remains, the annotation explicitly says that the rate is not verified. Do not invent a numeric replacement.

## Client Behavior

- Respect documented UID limits and any independently confirmed gateway limits.
- Do not configure IP token buckets from documentation group identifiers.
- On a rate-limit response, use bounded exponential backoff with jitter and honor retry guidance when supplied by the service.
- Do not blindly retry order placement or other writes after an ambiguous response; reconcile order state first.
- Keep REST endpoint policies separate from WebSocket connection and subscription policies. REST group identifiers do not specify WebSocket frame rates.

## Verification Boundary

A reported test on 2026-10-09 made 12 queries at approximately four requests per second, all with HTTP 200 and business code 0. This is limited evidence for that account, source IP, and time window, not proof of unrestricted access. A rate of 25 requests per second was not tested.

The correction is based on documentation source semantics and its changelog. Confirm current production policy with the API owner before raising traffic rates.

## Validation

The repository quality validator requires endpoint rate annotations and rejects the legacy IP rate wording derived from groups 2 and 3 in skill Markdown. If a future independently verified policy genuinely uses either rate, update this regression guard together with the supporting evidence.
