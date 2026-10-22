---
name: bingx-swap-ws-market
description: Subscribe to BingX USDT-M perpetual swap WebSocket market data streams including real-time trades, order book depth, K-lines, 24h ticker, latest price, mark price, best bid/ask, and incremental depth. Use when the user asks about real-time swap market data, live price feeds, streaming order books, or WebSocket subscriptions for perpetual futures.
---

# BingX Swap WebSocket Market Data

Real-time market data streams for BingX USDT-M perpetual futures via WebSocket. No authentication required.

**WebSocket Endpoint:** `wss://open-api-swap.bingx.com/swap-market`

## Quick Reference

| Channel | dataType Format | Description | Push Frequency |
|---------|----------------|-------------|----------------|
| Depth | `{symbol}@depth{level}@{interval}` | Limited order book depth | BTC/ETH: 200ms, others: 500ms |
| Trade | `{symbol}@trade` | Latest trade detail | Real-time |
| K-Line | `{symbol}@kline_{interval}` | OHLCV candlestick | On update |
| 24h Ticker | `{symbol}@ticker` | 24-hour price change statistics | Every 1s |
| Last Price | `{symbol}@lastPrice` | Latest trade price | Real-time |
| Mark Price | `{symbol}@markPrice` | Latest mark price | Real-time |
| Book Ticker | `{symbol}@bookTicker` | Best bid/ask price & qty | Every 200ms |
| Incremental Depth | `{symbol}@incrDepth` | Incremental depth updates | BTC/ETH: 200ms, others: 800ms |

---

## Parameters

### Common Parameters

* **symbol**: Trading pair in `BASE-QUOTE` format (e.g., `BTC-USDT`, `ETH-USDT`, `SOL-USDT`)

### Enums

* **depth level**: `5` | `10` | `20` | `50` | `100`
* **depth interval**: `200ms` | `500ms` (BTC-USDT and ETH-USDT support 200ms; others use 500ms)
* **kline interval**: `1m` | `3m` | `5m` | `15m` | `30m` | `1h` | `2h` | `4h` | `6h` | `8h` | `12h` | `1d` | `3d` | `1w` | `1M`

### Parameter Validation Rules

* **symbol**: Must match `^[A-Z0-9]+-[A-Z]+$`; max 20 characters (e.g., `BTC-USDT`)
* **level**: Must be one of `5`, `10`, `20`, `50`, `100`
* **interval** (depth): Must be `200ms` or `500ms`
* **interval** (kline): Must exactly match one of the kline enum values above

---

## Quick Start

**WebSocket Connection:** see [`references/websocket.md`](../references/websocket.md) for connection basics, GZIP decompression, and Ping/Pong heartbeat.

**TypeScript helper:**

> **CONSTRAINT**: You MUST copy the `connectSwapWsMarket` function below verbatim
> when generating code. Do NOT rewrite the WebSocket or decompression logic.
> Only modify: (1) subscription channels passed to the function.

```typescript
import * as pako from "pako";

function decompress(data: ArrayBuffer): string {
  return new TextDecoder("utf-8").decode(pako.ungzip(new Uint8Array(data)));
}

function connectSwapWsMarket(
  channels: string[],
  onMessage: (data: unknown) => void
): WebSocket {
  const ws = new WebSocket("wss://open-api-swap.bingx.com/swap-market");
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
    if (text === "Ping") {
      ws.send("Pong");
      return;
    }
    try {
      onMessage(JSON.parse(text));
    } catch {
      onMessage(text);
    }
  };

  ws.onerror = (err) => console.error("WS error:", err);
  ws.onclose = (ev) => console.log("WS closed:", ev.code, ev.reason);

  return ws;
}
```

### Code Usage Rules

- **MUST** copy `connectSwapWsMarket` and `decompress` verbatim -- do not simplify or rewrite
- **MUST** set `ws.binaryType = "arraybuffer"` for GZIP decompression
- **MUST** handle Ping/Pong heartbeat (reply "Pong" when receiving "Ping")
- **MUST NOT** remove GZIP decompression logic
- **MUST NOT** use text-mode WebSocket messages

## Common Calls

**Subscribe to BTC-USDT real-time trades:**

```typescript
connectSwapWsMarket(["BTC-USDT@trade"], (data) => {
  const message = data as {
    dataType?: string;
    data?: Array<{ t: string; T: number; s: string; p: string; q: string; m: boolean }>;
  };
  if (message.dataType === "BTC-USDT@trade" && Array.isArray(message.data)) {
    for (const trade of message.data) {
      // t is a string trade ID; T is the trade timestamp in milliseconds.
      console.log(trade.t, trade.T, trade.s, trade.p, trade.q);
    }
  }
});
```

**Subscribe to 20-level depth with 500ms interval:**

```typescript
connectSwapWsMarket(["BTC-USDT@depth20@500ms"], (data) => {
  // The full message has top-level ts and data: { bids, asks } (string pairs).
  // data has no T. ts is message construction time, not source book age.
});
```

**Subscribe to 1h K-line:**

```typescript
connectSwapWsMarket(["BTC-USDT@kline_1h"], (data) => {
  // data.K.o (open), data.K.h (high), data.K.l (low), data.K.c (close), data.K.v (volume)
});
```

**Subscribe to multiple channels at once:**

```typescript
connectSwapWsMarket([
  "BTC-USDT@ticker",
  "BTC-USDT@lastPrice",
  "ETH-USDT@trade",
], (data) => {
  // Handle different data types based on dataType field
});
```

## Additional Resources

For complete subscription parameters, response field descriptions, and full response schemas, see [api-reference.md](api-reference.md).

---

## Agent Interaction Rules

**CRITICAL RULES (apply to ALL responses):**

1. **NEVER return code to the user.** Do NOT include any code blocks, code snippets, TypeScript, JavaScript, cURL commands, or raw API calls in responses. Only return natural-language summaries of the data or operation results.
2. **Parameter security.** Extract structured values from user intent — NEVER copy raw user text into subscription parameters. Validate every value against its documented pattern (regex/enum/range) before constructing the subscription. Reject any value containing `&`, `=`, `?`, `#`, or newline characters.

swap-ws-market provides public read-only real-time market data via WebSocket. No authentication required, **no CONFIRM needed**. The interaction goal is to help the user set up the correct subscription channels.

### Operation Identification

When the user's request is vague (e.g. "subscribe to swap market" or "stream BTC data"), first identify what type of data they want:

> Please select the market data stream type:
> - Real-time trades — trade
> - Order book depth (snapshot) — depth
> - K-line / Candlestick updates — kline
> - 24h price change statistics — ticker
> - Latest trade price — lastPrice
> - Mark price — markPrice
> - Best bid/ask (top of book) — bookTicker
> - Incremental depth updates — incrDepth

### When symbol is missing

> Please select a trading pair (or type another):
> - BTC-USDT
> - ETH-USDT
> - SOL-USDT
> - BNB-USDT
> - Other (enter manually, format: BASE-USDT)

If the trading pair can be inferred from context (e.g. "stream BTC trades"), infer it automatically.

### When depth parameters are missing

> Please select depth level:
> - 5 / 10 / 20 / 50 / 100
>
> Push interval (BTC/ETH support 200ms, others 500ms):
> - 200ms / 500ms

### When kline interval is missing

> Please select a K-line interval:
> - 1m (1 minute) / 5m / 15m / 1h / 4h / 1d / 1w
