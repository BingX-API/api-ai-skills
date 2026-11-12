---
name: bingx-spot-ws-account
description: Subscribe to BingX spot WebSocket account data streams including order updates and balance changes. Also manages Listen Key lifecycle (generate, extend, delete). Use when the user asks about real-time spot account updates, live spot order status, streaming spot balance changes, or WebSocket account subscriptions for spot trading.
---

# BingX Spot WebSocket Account Data

Real-time account data streams for BingX spot trading via WebSocket. Requires Listen Key authentication.

**WebSocket Endpoint:** `wss://open-api-ws.bingx.com/market?listenKey=<key>`

Unlike swap account streams, spot account streams require **explicit channel subscription** after connecting.

## Quick Reference

### WebSocket Events (Require Subscription)

| Event Type | dataType | Description | Push Frequency |
|------------|----------|-------------|----------------|
| Order Update | `spot.executionReport` | Order creation, fills, cancellation | On change |
| Account Update | `ACCOUNT_UPDATE` | Account balance changes | On change |

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

Extends validity to 60 minutes. Recommended: call every 30 minutes.

### Delete Listen Key

```
DELETE /openApi/user/auth/userDataStream
```

**Parameters:** `listenKey` (string, required)

---

## Quick Start

**WebSocket Connection:** see [`references/websocket.md`](../references/websocket.md) for GZIP decompression and Ping/Pong heartbeat.

**TypeScript helper:**

> **CONSTRAINT**: You MUST copy the `connectSpotWsAccount` function below verbatim
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
    redirect: "error",
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

function connectSpotWsAccount(
  listenKey: string,
  channels: string[],
  onEvent: (event: any) => void
): WebSocket {
  const ws = new WebSocket(
    `wss://open-api-ws.bingx.com/market?listenKey=${listenKey}`
  );
  ws.binaryType = "arraybuffer";

  ws.onopen = () => {
    for (const ch of channels) {
      ws.send(JSON.stringify({
        id: crypto.randomUUID(),
        reqType: "sub",
        dataType: ch,
      }));
    }
  };

  ws.onmessage = (event) => {
    const text = decompress(event.data as ArrayBuffer);
    if (text.includes("ping") || text === "Ping") {
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

- **MUST** copy `connectSpotWsAccount`, `generateListenKey`, and `decompress` verbatim
- **MUST** explicitly subscribe to channels after connecting (unlike swap which auto-pushes)
- **MUST** handle Ping/Pong heartbeat
- **MUST** extend listen key every 30 minutes

## Common Calls

**Subscribe to order updates and account balance:**

```typescript
const listenKey = await generateListenKey(API_KEY, SECRET_KEY);
connectSpotWsAccount(listenKey, ["spot.executionReport", "ACCOUNT_UPDATE"], (event) => {
  if (event.dataType === "spot.executionReport") {
    // event.data: order update details
  } else if (event.e === "ACCOUNT_UPDATE") {
    // event.a.B: balance updates
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

spot-ws-account provides authenticated real-time account data. Requires Listen Key, **no CONFIRM needed for read-only monitoring**.

### Operation Identification

When the user's request is vague (e.g. "monitor my spot account"), clarify what they want:

> Please select the account data stream type:
> - Order updates (fills, cancellations, status) — spot.executionReport
> - Account balance changes — ACCOUNT_UPDATE
> - Both order and balance updates
> - Listen Key management (generate/extend/delete)

### Symbol context in account streams

Spot account events contain the relevant symbol in the push payload (e.g., `data.s` for order updates, `a.B[].a` for asset/balance updates). If the user asks about a specific symbol or asset, filter the events by the corresponding field. No symbol parameter is needed for subscription — subscribe to the event type and filter in the push data.
