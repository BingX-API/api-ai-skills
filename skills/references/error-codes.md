# API Error Code Reference

All BingX OpenAPI responses use `{ "code": <int>, "msg": "<string>", "data": ... }`. A `code` of `0` means success; any non-zero code indicates an error. This document lists all known error codes by category.

---

## HTTP Error Codes

HTTP-level status codes applicable to all endpoints.

| Code | Description |
|------|-------------|
| `400` | Bad Request — Invalid request format. |
| `401` | Unauthorized — Invalid API Key. |
| `403` | Forbidden — You do not have access to the requested resource. |
| `404` | Not Found — The requested resource does not exist. |
| `418` | Continued access after receiving 429, IP has been banned. Stop requests and wait. |
| `429` | Too Many Requests — Requests are too frequent, rate-limited by the system. |
| `500` | Internal Server Error — Internal server error. |
| `504` | Gateway Timeout — The server failed to get a response; further confirmation required. |

---

## Common Error Codes

Applies to all endpoints. Returned by the gateway layer before the request reaches backend services. Covers signature verification, API Key validation, IP whitelist, rate limiting, etc.

| Code | Description |
|------|-------------|
| `100001` | Request signature verification failed. Verify the signature algorithm, parameter order, and API secret. |
| `100004` | The API key does not have the required trading permission. Enable it in the API Key management page. |
| `100400` | Request routing error. Common reasons: API endpoint does not exist — verify the path in the API docs; Incorrect request method (GET/POST). |
| `100404` | The requested API path does not exist or the request method is incorrect. Verify the URL and method. |
| `100410` | Request rate limit exceeded. Reduce request frequency and retry after the cooldown period. |
| `100412` | Request is missing the signature parameter. Include a valid signature in your request. |
| `100413` | API Key is incorrect or missing. Ensure the API Key is correct and not deleted, and that `X-BX-APIKEY` is set in the HTTP request header. |
| `100419` | The request IP is not in the API Key IP whitelist. Check IP whitelist settings in the API Key management page. |
| `100421` | Null timestamp or timestamp mismatch with server time. Ensure your local clock is synchronized. |
| `100500` | System busy. Please retry later. |

---

## Futures Error Codes

Errors related to USDT-M and Coin-M perpetual futures (swap and cswap endpoints).

| Code | Description |
|------|-------------|
| `101201` | The current position is too large for the requested leverage. Reduce position size before adjusting. |
| `101202` | Order value is below the contract minimum. Increase the order value; query contract info for the minimum. |
| `101204` | Insufficient margin to place the order. Add margin, lower leverage, or reduce order size. |
| `101205` | No position exists to close. Query positions first to confirm a position exists. |
| `101206` | Account available balance is insufficient. Add funds and retry. |
| `101209` | The maximum position value for the current leverage has been reached. Lower leverage or reduce order size. |
| `101210` | Account belongs to a restricted region or account status is abnormal. Verify account status or contact support. |
| `101211` | Order price exceeds the allowed range (too high or too low). Adjust the price to within the allowed range. |
| `101212` | Available balance is insufficient for this order. Reduce order amount or add funds. |
| `101214` | Funding fee settlement is in progress. Retry in a few seconds. |
| `101215` | Post Only order was cancelled because it would have been filled immediately. Adjust the price or use a different order type. |
| `101219` | Account assets are being processed and temporarily unavailable. Please retry later. |
| `101222` | Current leverage risk is too high. Lower leverage and retry. |
| `101253` | Insufficient margin (including adjustable margin). Add funds or reduce order notional. |
| `101290` | A Reduce Only order can only decrease an existing position. Ensure the order does not exceed the current position size. |
| `101400` | Order parameter validation failed. Possible reasons: order amount or quantity below minimum; TP/SL price does not match position direction; duplicate clientOrderID; trading pair suspended. |
| `101412` | Account information has changed. Please refresh and try again. |
| `101413` | Currently in non-trading hours. Retry during trading hours. |
| `101414` | Leverage exceeds limit — may exceed maximum for the trading pair, be restricted during certain periods, or non-crypto contracts may not support OpenAPI one-way mode. |
| `101415` | This trading pair is suspended from opening positions or trading. Check announcements for resumption. |
| `101419` | Pending orders reached the upper limit. Cancel some pending orders first. |
| `101429` | This order exceeds the current position limit. Reduce order size or check the position limit. |
| `101434` | Trial Fund accounts cannot hold both long and short positions. Close existing position first. |
| `101460` | For long positions, the order price must be higher than the estimated liquidation price. |
| `101461` | For short positions, the order price must be lower than the estimated liquidation price. |
| `101479` | The position is not in Isolated Margin Mode. Switch to Isolated Margin Mode first. |
| `101481` | The clientOrderID has already been used. Use a unique clientOrderID for each new order. |
| `101483` | Advanced identity verification (KYC) is required to use this feature. |
| `101484` | Account belongs to a restricted region or advanced identity verification is required. |
| `101485` | The closing order size is below the minimum. Increase the closing size. |
| `102201` | Order was canceled because filling it may result in negative account assets. Add margin or reduce order size. |
| `104103` | Cannot switch position mode while positions or pending orders exist. Close all positions and cancel all orders first. |
| `104108` | One-way position mode does not support separate isolated margin mode. Switch to Hedge mode first. |
| `104414` | This feature is not available for copy trading lead traders. Use a non-lead-trader account. |
| `104424` | Currently in non-trading hours. Retry during trading hours. |
| `109201` | The same order number was submitted more than once in a short period. Use a unique clientOrderID. |
| `109400` | Invalid request parameters. Common reasons: symbol format error (must end with -USDT or -USDC); missing required parameters (symbol / timestamp / side / type, etc.); parameter value out of allowed range (limit, interval, positionSide, etc.); invalid or skewed timestamp; query time range exceeds limit (e.g. 7 days or 90 days); position mode mismatch (e.g. PositionSide must be BOTH in one-way mode). |
| `109403` | Request blocked by risk control — rate too high or cancellation rate exceeded. Fix the request and retry after the restriction period. |
| `109417` | This trading pair is in pre-launch status and not yet open. Check the contract list for opening time. |
| `109420` | No position exists for the specified symbol. Query position information first. |
| `109421` | The specified order does not exist — it may have been filled, cancelled, or the order ID is incorrect. |
| `109425` | The trading pair does not exist or is not supported. Call /openApi/swap/v2/quote/contracts to verify. |
| `109429` | Too many invalid requests in a short period; temporarily restricted. Fix the root cause and retry later. |
| `109430` | The account has pending TWAP orders. Wait for or cancel existing TWAP orders first. |
| `109500` | Internal server error. If it persists, please retry later or contact support. |
| `109701` | Network request exception. Check your network connection and retry. |
| `110203` | Available amount for closing is insufficient. Reduce closing quantity or wait for pending orders to fill. |
| `110206` | TP/SL orders reached the maximum limit. Cancel some existing TP/SL orders first. |
| `110280` | This trading pair is suspended from opening positions. Check announcements for resumption. |
| `110284` | The Guaranteed Stop Loss feature is not available for this trading pair or account. |
| `110287` | The maximum position value for the current leverage has been reached. Lower leverage or reduce order size. |
| `110400` | The submitted order parameters do not meet the requirements. Verify price, quantity, etc. |
| `110402` | Order price is invalid — must be greater than the minimum price. Adjust the order price. |
| `110406` | A Stop Loss order already exists for this position. Cancel the existing one first. |
| `110407` | A Take Profit order already exists for this position. Cancel the existing one first. |
| `110411` | For long positions, the Stop Loss price should be lower than the current price. |
| `110412` | For short positions, the Stop Loss price should be greater than the current price. |
| `110413` | For long positions, the Take Profit price should be greater than the current price. |
| `110414` | For short positions, the Take Profit price should be lower than the current price. |
| `110415` | The trailing stop callback rate is below the minimum. Increase the callback rate. |
| `110418` | The trailing stop distance exceeds the maximum. Decrease the trailing distance. |
| `110419` | For short trailing stops, the activation price must be greater than the Last/Mark Price. |
| `110420` | For long trailing stops, the activation price must be lower than the Last/Mark Price. |
| `110422` | The order size is below the minimum per-order requirement. Increase the order size. |
| `110424` | Order size exceeds available balance. Reduce order size or add funds. |
| `110425` | Order size does not meet the contract precision or step size requirement. |
| `110426` | The submitted order parameters do not meet the requirements. Verify and retry. |
| `110427` | The SL limit price is below the allowed minimum. Increase the SL limit price. |
| `110428` | The SL limit price is above the allowed maximum. Decrease the SL limit price. |
| `110500` | Order system busy. Please retry later. |
| `112414` | The total position amount has reached the platform limit. Reduce existing positions first. |

---

## Spot Error Codes

Errors returned by spot market data and trading endpoints.

| Code | Description |
|------|-------------|
| `100202` | Account balance is insufficient. Add funds and retry. |
| `100204` | Requested data not found. Common reasons: symbol does not exist or is misspelled; no kline or trade data in the queried time range; query time span is too wide. |
| `100400` | Request parameter error or resource not found. Common reasons: missing required parameter (e.g. timestamp); invalid symbol format (should be like BTC-USDT); invalid interval value; order does not exist. |
| `100404` | Order does not exist. The order may have been filled or cancelled. |
| `100410` | Too many erroneous requests in a short period, triggering rate limit. Fix parameters and retry. |
| `100421` | Request rejected. Common reasons: LIMIT pending orders reached max (1000); trading pair not available for API orders. |
| `100440` | Order price deviates too much from market price, triggering price protection. Adjust the price. |
| `100441` | Account is abnormal or advanced identity verification is required. Complete KYC or contact support. |
| `100490` | Spot trading pair is offline. Check status via /openApi/spot/v1/common/symbols. |
| `100500` | System busy or query failed. Please retry later. |
| `101402` | This account does not support trading of this pair. Verify account permissions and pair status. |

---

## Account / Wallet / Agent Error Codes

Errors returned by account management, wallet deposit/withdrawal, sub-account, and agent endpoints.

| Code | Description |
|------|-------------|
| `100202` | Insufficient assets. Add funds and retry. |
| `100400` | Invalid request parameters. Common reasons: amount must be greater than 0; main account does not exist; missing required parameter (e.g. uid). |
| `100403` | The current account is not the main account. This endpoint is restricted to main accounts only. |
| `100437` | Coin does not exist or deposit address query failed. Verify the coin name. |
| `100450` | The current account information is incorrect (e.g. invalid sub-account UID). |
| `100500` | System busy. Please retry later. |
