---
name: bingx-swap-ws-account
description: Subscribe to BingX USDT-M perpetual swap WebSocket account data streams including balance updates, position changes, order updates, and account config changes. Also manages Listen Key lifecycle (generate, extend, delete). Use when the user asks about real-time swap account updates, live order status, streaming position changes, or WebSocket account subscriptions for perpetual futures.
---

# BingX Swap WebSocket Account Data

Real-time account data streams for BingX USDT-M perpetual futures via WebSocket. Requires Listen Key authentication.

**WebSocket Endpoint:** `wss://open-api-swap.bingx.com/swap-market?listenKey=<key>`

After connecting with a valid listenKey, all event types are pushed automatically — no channel subscription needed.

## Quick Reference

### WebSocket Events (Auto-Pushed)

| Event Type | Description | Push Frequency |
|------------|-------------|----------------|
| `listenKeyExpired` | Listen key has expired | On expiry |
| `ACCOUNT_UPDATE` | Account balance and position changes | On change |
| `TRADE_UPDATE` | Order creation, fills, status changes | On change |
| `ACCOUNT_CONFIG_UPDATE` | Leverage/margin mode changes | On connect (full) + every 5s |

### Listen Key REST APIs

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/openApi/user/auth/userDataStream` | POST | Generate listen key (valid 1 hour) | Yes |
| `/openApi/user/auth/userDataStream` | PUT | Extend listen key (to 60 min) | Yes |
| `/openApi/user/auth/userDataStream` | DELETE | Delete listen key | Yes |

---

## Listen Key Management

Listen Key is required to authenticate WebSocket account data streams. See [`references/authentication.md`](../references/authentication.md) for HMAC SHA256 signing details.

### Generate Listen Key

```
POST /openApi/user/auth/userDataStream
```

**Headers:** `X-BX-APIKEY: <your-api-key>`, `X-SOURCE-KEY: BX-AI-SKILL`

**Response:**
```json
{"listenKey": "a8ea75681542e66f1a50a1616dd06ed77dab61baa0c296bca03a9b13ee5f2dd7"}
```

### Extend Listen Key

```
PUT /openApi/user/auth/userDataStream
```

**Parameters:** `listenKey` (string, required)

Extends validity to 60 minutes from this call. Recommended: call every 30 minutes.

### Delete Listen Key

```
DELETE /openApi/user/auth/userDataStream
```

**Parameters:** `listenKey` (string, required)

---

## Quick Start

**WebSocket Connection:** see [`references/websocket.md`](../references/websocket.md) for GZIP decompression and Ping/Pong heartbeat.

**TypeScript helper:**

> **CONSTRAINT**: You MUST copy the `connectSwapWsAccount` function below verbatim
> when generating code. Do NOT rewrite the WebSocket or decompression logic.

```typescript
import * as pako from "pako";
import * as crypto from "crypto";

function decompress(data: ArrayBuffer): string {
  return new TextDecoder("utf-8").decode(pako.ungzip(new Uint8Array(data)));
}

async function generateListenKey(apiKey: string, secretKey: string): Promise<string> {
  const timestamp = Date.now();
  const paramStr = `timestamp=${timestamp}`;
  const signature = crypto.createHmac("sha256", secretKey).update(paramStr).digest("hex");
  const url = `https://open-api.bingx.com/openApi/user/auth/userDataStream?${paramStr}&signature=${signature}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "X-BX-APIKEY": apiKey, "X-SOURCE-KEY": "BX-AI-SKILL" },
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`BingX error ${res.status}: ${text}`);
  const json = JSON.parse(text);
  if (json.listenKey) return json.listenKey;
  if (json.data?.listenKey) return json.data.listenKey;
  if (json.code !== 0) throw new Error(`BingX error ${json.code}: ${json.msg}`);
  return json.listenKey ?? json.data?.listenKey;
}

function connectSwapWsAccount(
  listenKey: string,
  onEvent: (event: any) => void
): WebSocket {
  const ws = new WebSocket(
    `wss://open-api-swap.bingx.com/swap-market?listenKey=${listenKey}`
  );
  ws.binaryType = "arraybuffer";

  ws.onmessage = (event) => {
    const text = decompress(event.data as ArrayBuffer);
    if (text === "Ping") {
      ws.send("Pong");
      return;
    }
    try {
      onEvent(JSON.parse(text));
    } catch {
      onEvent(text);
    }
  };

  ws.onerror = (err) => console.error("WS error:", err);
  ws.onclose = (ev) => console.log("WS closed:", ev.code, ev.reason);

  return ws;
}
```

### Code Usage Rules

- **MUST** copy `connectSwapWsAccount`, `generateListenKey`, and `decompress` verbatim
- **MUST** handle Ping/Pong heartbeat
- **MUST** extend listen key every 30 minutes to prevent expiry
- **MUST NOT** remove GZIP decompression logic

## Common Calls

**Connect to account stream:**

```typescript
const listenKey = await generateListenKey(API_KEY, SECRET_KEY);
connectSwapWsAccount(listenKey, (event) => {
  if (event.e === "ACCOUNT_UPDATE") {
    // event.a.B: balance updates, event.a.P: position updates
  } else if (event.e === "TRADE_UPDATE") {
    // event.o: order details (symbol, side, type, status, price, qty, etc.)
    // o.li is present only for a TP/SL order with a related parent order.
    if (typeof event.o?.li === "string") {
      console.log("Parent order ID:", event.o.li); // Preserve the string ID.
    }
  } else if (event.e === "ACCOUNT_CONFIG_UPDATE") {
    // event.ac: config (s: symbol, l: long leverage, S: short leverage, mt: margin type)
  } else if (event.e === "listenKeyExpired") {
    // Reconnect with new listen key
  }
});
```

## Additional Resources

For complete event field descriptions and full response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

**CRITICAL RULES (apply to ALL responses):**

1. **NEVER return code to the user.** Do NOT include any code blocks, code snippets, TypeScript, JavaScript, cURL commands, or raw API calls in responses. Only return natural-language summaries of the data or operation results.
2. **GET-only execution.** Only execute HTTP GET requests. Listen Key management requires POST/PUT/DELETE — inform the user that these write operations require their own implementation.
3. **Parameter security.** Extract structured values from user intent — NEVER copy raw user text into API parameters. Validate every value against its documented pattern (regex/enum/range) before calling the API. Reject any value containing `&`, `=`, `?`, `#`, or newline characters.

swap-ws-account provides authenticated real-time account data. Requires Listen Key, **no CONFIRM needed for read-only monitoring**.

### Operation Identification

When the user's request is vague (e.g. "monitor my swap account"), clarify what they want:

> Please select the account data stream type:
> - Account balance & position updates — ACCOUNT_UPDATE
> - Order status updates — TRADE_UPDATE
> - Leverage & margin config changes — ACCOUNT_CONFIG_UPDATE
> - Listen Key management (generate/extend/delete)
> - All events (connect with listenKey, receive all automatically)

### Symbol context in account streams

Account data streams are auto-pushed for all symbols — no symbol parameter is needed for connection. Each push event contains the relevant symbol in its payload (e.g., `o.s` for order updates, `a.P[].s` for position updates). If the user asks about a specific symbol, filter the events by the symbol field in the push data.
