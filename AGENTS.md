# BingX AI Skills — Agent Instructions

This is a **BingX OpenAPI skill collection** providing 22 skills for perpetual contract, spot, coin-margined, copy trading, account operations, announcements, and WebSocket real-time data streams: market data queries, trading operations, account management, wallet operations, copy trading, sub-account management, agent/affiliate management, official announcements, and WebSocket market/account data subscriptions.

## Available Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| bingx-swap-market | Perpetual futures market data | User asks for swap price, depth, K-lines, funding rate, contract info, ticker, open interest, or any perpetual futures market data queries |
| bingx-swap-trade | Perpetual futures trading | User wants to place swap orders, cancel swap orders, modify orders, set leverage, set margin mode, query swap orders, or any swap trading operations |
| bingx-swap-account | Perpetual futures account | User asks for swap balance, positions, assets, income history, funding history, commission rate, or swap account information |
| bingx-spot-market | Spot market data | User asks for spot price, spot order book, spot K-lines, spot recent trades, spot trading symbols, or any spot market data queries |
| bingx-spot-trade | Spot trading | User wants to place spot orders, cancel spot orders, query spot open orders or order history, view trade fills, manage OCO orders, or check spot trading commission rates |
| bingx-spot-account | Spot account management | User asks for spot balance, asset overview, or wants to transfer assets between accounts |
| bingx-spot-wallet | Spot wallet operations | User wants to deposit, withdraw, query deposit/withdrawal history, or check coin network configuration |
| bingx-coinm-market | Coin-M perpetual market data | User asks for coin-margined perpetual futures price, depth, K-lines, funding rate, or market statistics |
| bingx-coinm-trade | Coin-M perpetual trading | User wants to place/cancel coin-margined perpetual orders, set leverage/margin mode, or manage positions |
| bingx-copytrade-spot | Spot copy trading | User wants to manage spot copy trading, sell copy trade positions, or query spot copy trading profit |
| bingx-copytrade-swap | Swap copy trading | User wants to manage perpetual contract copy trading, close copy trade positions, or set TP/SL on copy trades |
| bingx-fund-account | Fund account management | User asks about main account funds, asset overview, or fund transfers between accounts |
| bingx-sub-account | Sub-account management | User wants to create/list sub-accounts, manage sub-account API keys, freeze/unfreeze accounts, or transfer assets between sub-accounts |
| bingx-agent | Agent/affiliate management | User asks about agent invited users, affiliate commissions, referral relationships, partner data, or broker commission reports |
| bingx-standard-trade | Standard contract trading | User asks about standard contract positions, standard futures order history, or standard contract balance |
| bingx-announcement | Official announcements | User asks about BingX announcements, notices, promotions, product updates, maintenance notices, listing/delisting, or funding rate notices |
| bingx-swap-ws-market | Swap WebSocket market data | User asks for real-time swap market data, live perpetual futures price feeds, streaming swap order books, WebSocket depth/trade/kline/ticker subscriptions for perpetual futures |
| bingx-swap-ws-account | Swap WebSocket account data | User asks for real-time swap account updates, live order status streaming, position change notifications, or WebSocket account monitoring for perpetual futures |
| bingx-spot-ws-market | Spot WebSocket market data | User asks for real-time spot market data, live spot price feeds, streaming spot order books, WebSocket depth/trade/kline/ticker subscriptions for spot trading |
| bingx-spot-ws-account | Spot WebSocket account data | User asks for real-time spot account updates, live spot order status streaming, spot balance change notifications, or WebSocket account monitoring for spot trading |
| bingx-coinm-ws-market | Coin-M WebSocket market data | User asks for real-time coin-margined futures market data, live Coin-M price feeds, streaming inverse futures order books, or WebSocket subscriptions for coin-margined perpetual futures |
| bingx-coinm-ws-account | Coin-M WebSocket account data | User asks for real-time Coin-M account updates, live coin-margined order status, inverse futures position changes, or WebSocket account monitoring for coin-margined perpetual futures |
| bingx-technical-analysis | Technical analysis | User asks for technical analysis, indicator values (RSI, MACD, EMA, Bollinger Bands, etc.), candlestick pattern recognition, multi-timeframe scoring, support/resistance levels, or divergence detection |
| bingx-rsi-bottom-hunter | RSI bottom-fishing strategy | User asks for RSI bottom fishing, oversold buying, RSI strategy, or wants to auto-monitor RSI and execute trades when oversold conditions are met |
| bingx-maker-entry | Maker limit order entry | User wants to open a position using limit orders, save taker fees, place multi-level limit orders near best price, or dynamically adjust orders as price moves |
| bingx-trade-review | Trade review and performance analysis | User asks for trade review, PnL summary, win rate, trade journal, custom trade tags, or cross-period performance comparison |
| bingx-dynamic-sl-tp | Dynamic stop-loss and take-profit | User asks to set, adjust, or optimize stop-loss and take-profit using ATR, volatility, or structure-based strategies; supports trailing stop, partial take-profit, and break-even stop |

## Skill Discovery

Skills are in the `skills/` directory. Each skill contains a `SKILL.md` with:

- YAML frontmatter (name, description, metadata)
- Full API reference with endpoints, parameters, and response schemas
- Code examples (TypeScript)
- Authentication implementation (HMAC SHA256)
- Error handling and edge cases

## Authentication

All trading and account APIs require HMAC SHA256 authentication with:
- API Key (set via `BINGX_API_KEY` environment variable)
- Secret Key (set via `BINGX_SECRET_KEY` environment variable)

Market data APIs (bingx-swap-market, bingx-spot-market, bingx-coinm-market), the announcement API (bingx-announcement), and WebSocket market data streams (bingx-swap-ws-market, bingx-spot-ws-market, bingx-coinm-ws-market) do NOT require authentication.

WebSocket account data streams (bingx-swap-ws-account, bingx-spot-ws-account, bingx-coinm-ws-account) require a Listen Key obtained via the REST API `/openApi/user/auth/userDataStream` (POST to generate, PUT to extend, DELETE to delete). The Listen Key is valid for 1 hour and should be extended every 30 minutes.

**Mandatory Header**: ALL requests (including unauthenticated market data requests) MUST include the header `X-SOURCE-KEY: BX-AI-SKILL`. This header identifies the request source. Never omit it.

## Safety & Confirmation

For production live trading environment (`prod-live`), all write operations (place order, cancel order, etc.) require user confirmation by typing **CONFIRM**. Test and simulation environments do not require confirmation.

## WebSocket Endpoints

WebSocket skills provide real-time data streaming via persistent connections:

| Product Line | Market Data (Public) | Account Data (Authenticated) |
|-------------|---------------------|------------------------------|
| USDT-M Perpetual | `wss://open-api-swap.bingx.com/swap-market` | `wss://open-api-swap.bingx.com/swap-market?listenKey=<key>` |
| Spot | `wss://open-api-ws.bingx.com/market` | `wss://open-api-ws.bingx.com/market?listenKey=<key>` |
| Coin-M Perpetual | `wss://open-api-cswap-ws.bingx.com/market` | `wss://open-api-cswap-ws.bingx.com/market?listenKey=<key>` |

All WebSocket messages are GZIP compressed. Server sends heartbeat messages (Swap: exact string `Ping`; Spot/Coin-M: may contain lowercase `ping`); client must reply `Pong` to keep the connection alive.

## Multi-Skill Workflows

Skills work together for complete trading workflows:

**Swap Market Research → Trading**: `bingx-swap-market` (get price/depth) → `bingx-swap-account` (check balance) → `bingx-swap-trade` (place order)

**Position Management**: `bingx-swap-account` (check positions) → `bingx-swap-trade` (close position) → `bingx-swap-account` (verify closure)

**Swap Account Review**: `bingx-swap-account` (get balance/positions) → `bingx-swap-market` (check current prices) → analyze PnL

**Spot Trading**: `bingx-spot-market` (get spot price/depth) → `bingx-spot-account` (check spot balance) → `bingx-spot-trade` (place spot order)

**Asset Transfer**: `bingx-spot-account` (check spot balance) → `bingx-spot-account` (transfer to futures) → `bingx-swap-trade` (place swap order)

**Coin-M Trading**: `bingx-coinm-market` (get price/depth) → `bingx-coinm-trade` (place order)

**Copy Trading**: `bingx-copytrade-swap` (query current positions) → `bingx-copytrade-swap` (close/set TP/SL)

**Real-Time Swap Monitoring**: `bingx-swap-ws-market` (subscribe to live price/depth) + `bingx-swap-ws-account` (monitor positions/orders in real-time)

**Real-Time Spot Monitoring**: `bingx-spot-ws-market` (subscribe to live spot price/depth) + `bingx-spot-ws-account` (monitor spot orders/balance in real-time)

**Real-Time Coin-M Monitoring**: `bingx-coinm-ws-market` (subscribe to live Coin-M price/depth) + `bingx-coinm-ws-account` (monitor positions/orders in real-time)

**REST + WebSocket Combo**: `bingx-swap-market` (query historical klines) → `bingx-swap-ws-market` (subscribe to real-time kline updates for continuous monitoring)
