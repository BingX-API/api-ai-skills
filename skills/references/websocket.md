# BingX WebSocket 连接规范

本文档描述所有 BingX WebSocket skill 共用的连接规范，包括消息压缩、心跳机制、订阅格式和 Listen Key 生命周期管理。

---

## WebSocket 端点

| 产品线 | 行情数据（公开） | 账户数据（需 listenKey） |
|--------|-----------------|------------------------|
| USDT-M 永续合约 | `wss://open-api-swap.bingx.com/swap-market` | `wss://open-api-swap.bingx.com/swap-market?listenKey=<key>` |
| 现货 | `wss://open-api-ws.bingx.com/market` | `wss://open-api-ws.bingx.com/market?listenKey=<key>` |
| 币本位永续合约 | `wss://open-api-cswap-ws.bingx.com/market` | `wss://open-api-cswap-ws.bingx.com/market?listenKey=<key>` |

---

## GZIP 解压

所有 WebSocket 推送消息均经过 **GZIP 压缩**。客户端收到二进制帧后，必须先进行 GZIP 解压，再按 UTF-8 解码为字符串。

```typescript
import * as pako from "pako";

function decompress(data: ArrayBuffer): string {
  const decompressed = pako.ungzip(new Uint8Array(data));
  return new TextDecoder("utf-8").decode(decompressed);
}
```

---

## Ping/Pong 心跳

服务端会定期发送文本消息 `Ping`（解压后的字符串）。客户端收到后 **必须** 立即回复文本消息 `Pong`，否则连接将被服务端断开。

```typescript
ws.onmessage = (event) => {
  const text = decompress(event.data);
  if (text === "Ping") {
    ws.send("Pong");
    return;
  }
  // 处理业务消息...
};
```

> **注意**：Swap 端点的心跳消息为精确字符串 `Ping`（首字母大写）；Spot 和 Coin-M 端点可能包含小写形式，建议用 `text.includes("ping") || text === "Ping"` 进行匹配。

---

## 订阅消息格式

行情数据流需要通过发送 JSON 消息进行订阅/取消订阅。

### 订阅请求

```json
{
  "id": "unique-request-id",
  "reqType": "sub",
  "dataType": "BTC-USDT@trade"
}
```

### 取消订阅请求

```json
{
  "id": "unique-request-id",
  "reqType": "unsub",
  "dataType": "BTC-USDT@trade"
}
```

### 参数说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 请求唯一标识符，可使用 UUID |
| reqType | string | 是 | `sub` 订阅 / `unsub` 取消订阅 |
| dataType | string | 是 | 订阅频道标识，格式为 `{symbol}@{channel}`，交易对中必须包含连字符 `-` |

### dataType 格式示例

- `BTC-USDT@trade` -- 逐笔成交
- `BTC-USDT@kline_1m` -- 1 分钟 K 线
- `BTC-USDT@depth20@500ms` -- 20 档深度，500ms 推送
- `BTC-USDT@ticker` -- 24h 行情
- `BTC-USDT@lastPrice` -- 最新成交价
- `BTC-USDT@markPrice` -- 标记价格
- `BTC-USDT@bookTicker` -- 最优挂单
- `BTC-USDT@incrDepth` -- 增量深度

> **币本位合约**使用 `BTC-USD` 格式（非 `BTC-USDT`）。

---

## Listen Key 生命周期

账户数据流需要通过 Listen Key 鉴权。Listen Key 通过 REST API 管理：

| 操作 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 生成 | POST | `/openApi/user/auth/userDataStream` | 返回 listenKey，有效期 1 小时 |
| 延期 | PUT | `/openApi/user/auth/userDataStream` | 延长有效期至 60 分钟，建议每 30 分钟调用一次 |
| 删除 | DELETE | `/openApi/user/auth/userDataStream` | 主动删除 listenKey |

### 关键注意事项

- Listen Key **有效期 1 小时**，过期后连接将收到 `listenKeyExpired` 事件推送
- 建议每 **30 分钟** 调用延期接口保活
- 生成/延期/删除操作均需要 HMAC SHA256 签名鉴权（参见 [`authentication.md`](authentication.md)）
- 请求头必须携带 `X-BX-APIKEY`

---

## USDT-M Incremental Depth

For USDT-M `{symbol}@incrDepth`, follow the [channel-specific initialization and recovery rules](../swap-ws-market/api-reference.md#how-to-maintain-incremental-depth-locally). Initialize only from an actual `action=all` snapshot on the connection carrying the active subscription. For recovery, prefer a new connection and wait for its snapshot; snapshot delivery is not guaranteed. Old-connection snapshots, unsubscribe-phase snapshots, and acknowledgements do not establish recovery. `lastUpdateId` alone cannot verify completeness; a fixed-size buffer cannot guarantee recovery.

These rules are not a shared sequencing contract for Spot or Coin-M. Consult each product's reference separately; do not extrapolate USDT-M behavior to other channels.

---

## TypeScript WebSocket Helper

> **约束**：生成代码时 MUST 原样复制以下 `connectBingXWS` 函数。
> 仅允许修改：(1) WSS URL，(2) 订阅频道参数。

```typescript
import * as pako from "pako";

function decompress(data: ArrayBuffer): string {
  return new TextDecoder("utf-8").decode(pako.ungzip(new Uint8Array(data)));
}

function connectBingXWS(
  url: string,
  channels: string[],
  onMessage: (data: unknown) => void
): WebSocket {
  const ws = new WebSocket(url);
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
    if (text === "Ping" || text.includes("ping")) {
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

### 代码使用规则

- **MUST** 原样复制 `connectBingXWS` 和 `decompress` 函数
- **MUST** 设置 `ws.binaryType = "arraybuffer"` 以便 GZIP 解压
- **MUST** 处理 Ping/Pong 心跳
- **MUST NOT** 移除 GZIP 解压逻辑
- **MUST NOT** 使用文本模式接收消息
