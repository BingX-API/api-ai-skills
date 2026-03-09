# BingX OpenAPI Skills

> A BingX Exchange API Skills Library for AI coding assistants — 15 skill modules covering perpetual futures, spot trading, coin-margined contracts, copy trading, and account management.

Once installed, you can interact with the AI using natural language to query market data, place trades, and manage accounts — no manual API coding required.

**Supported AI Assistants**: OpenClaw、Claude Code, Cursor, and other AI coding assistants that support the skills mechanism.

---

## Quick Start

### Method 1: AI Conversation Install (Recommended)

**Works with OpenClaw, Cursor, Claude Code, and other AI coding assistants**

Simply tell your AI:

> Set up the skills https://github.com/BingX-API/api-ai-skills

The AI will automatically recognize and complete the installation, no commands needed!

---

### Method 2: Claude Code Plugin Install

```bash
/plugin marketplace add BingX-API/api-ai-skills
/plugin install bingx-ai-skills
```

---

### Method 3: NPX Command Install

```bash
npx skills add BingX-API/api-ai-skills
```

**Works with** Cursor, Windsurf, and other AI assistants that support the skills mechanism

---

## Usage After Installation

After installation, the AI assistant will automatically recognize the following skills:

**USDT-M Perpetual Futures**:
- **bingx-swap-market** — Query perpetual futures market data (price, depth, klines, funding rate, open interest, etc.)
- **bingx-swap-trade** — Perpetual futures trading operations (place/cancel orders, set leverage, margin mode, etc.)
- **bingx-swap-account** — Query account info (balance, positions, commission rate, fund flow, etc.)

**Spot Trading**:
- **bingx-spot-market** — Query spot market data (price, depth, klines, recent trades, etc.)
- **bingx-spot-trade** — Spot trading operations (place/cancel orders, order queries, OCO orders, etc.)
- **bingx-spot-account** — Query spot account info (balance, asset overview, asset transfers, etc.)
- **bingx-spot-wallet** — Wallet operations (deposit, withdraw, transfer records, etc.)

**Coin-M Perpetual Futures**:
- **bingx-coinm-market** — Query coin-margined futures market data (price, depth, klines, funding rate, etc.)
- **bingx-coinm-trade** — Coin-margined futures trading operations (place/cancel orders, leverage, margin mode, etc.)

**Copy Trading**:
- **bingx-copytrade-spot** — Spot copy trading (sell copy positions, query profit, etc.)
- **bingx-copytrade-swap** — Futures copy trading (close positions, set TP/SL, commission settings, etc.)

**Account Management**:
- **bingx-fund-account** — Fund account management (balance query, asset overview, inter-account transfers, etc.)
- **bingx-sub-account** — Sub-account management (create/freeze sub-accounts, API key management, etc.)
- **bingx-agent** — Agent/broker (invited users, commission queries, partner data, etc.)

**Standard Contract**:
- **bingx-standard-trade** — Standard contract (position query, order history, balance query, etc.)

---

## Authentication

### Skills That Do NOT Require Auth

The following market data skills can be used **without an API key**:

- `bingx-swap-market` (perpetual futures market data)
- `bingx-spot-market` (spot market data)
- `bingx-coinm-market` (coin-margined futures market data)

### Skills That Require Auth

All other trading and account skills require the following environment variables:

- `BINGX_API_KEY` — Your API Key
- `BINGX_SECRET_KEY` — Your Secret Key

Create your API Key at [BingX User Center → API Management](https://bingx.com/en/accounts/api).

### Environments

| Environment | Description | Primary URL | Fallback URL |
|-------------|-------------|-------------|--------------|
| `prod-live` | Production (real funds) | `https://open-api.bingx.com` | `https://open-api.bingx.pro` |
| `prod-vst` | Simulated trading (testnet) | `https://open-api-vst.bingx.com` | `https://open-api-vst.bingx.pro` |

> For full authentication technical details, see [skills/references/authentication.md](skills/references/authentication.md)

---

## Usage Examples

After installation, you can talk to the AI in natural language. Here are 3 typical scenarios:

### Example 1: USDT-M Perpetual Futures Order

```
Place a BTC-USDT USDT-M perpetual market buy order on BingX, go long 0.01 BTC
```

> The AI will use the `bingx-swap-trade` skill to build a signed request and submit the order. In the `prod-live` environment, you will be asked to type **CONFIRM** before execution.

### Example 2: USDT-M Kline Query

```
Query the ETH-USDT USDT-M perpetual klines on BingX for the last 4 hours, 15-minute interval
```

> The AI will use the `bingx-swap-market` skill to fetch kline data. This endpoint requires no authentication and returns results directly.

### Example 3: Spot Order

```
Market buy 50 USDT worth of BTC-USDT on BingX spot market
```

> The AI will use the `bingx-spot-trade` skill to place the order. Spot market buy orders use the `quoteOrderQty` parameter to specify the spending amount.

---

## About

This repository is a Skills collection designed for **AI coding assistants**, enabling AI to directly understand and call [BingX Exchange](https://bingx.com) REST APIs without users having to write request code manually.

### How Skills Work

Each skill module consists of two files:

- **`SKILL.md`** — Agent behavior instructions
  - Module purpose and quick reference table
  - TypeScript code examples
  - Agent interaction rules (authentication, confirmation flow, etc.)

- **`api-reference.md`** — Complete API documentation
  - Parameter descriptions and response fields
  - Example JSON and error codes

After reading these files, the AI can autonomously handle HMAC SHA256 signing, request construction, and response parsing, allowing users to query market data, place trades, and manage accounts through natural language.

---

## Skill Overview

### USDT-M Perpetual Futures

| Skill | Purpose | Auth Required |
|-------|---------|---------------|
| `bingx-swap-market` | Market data: price, depth, klines, funding rate, open interest, etc. | No |
| `bingx-swap-trade` | Trading: place/cancel orders, set leverage, margin mode, etc. | Yes |
| `bingx-swap-account` | Account: balance, positions, commission rate, fund flow, etc. | Yes |

### Spot Trading

| Skill | Purpose | Auth Required |
|-------|---------|---------------|
| `bingx-spot-market` | Market data: price, depth, klines, recent trades, etc. | No |
| `bingx-spot-trade` | Trading: place/cancel orders, order queries, OCO orders, etc. | Yes |
| `bingx-spot-account` | Account: balance, asset overview, asset transfers, etc. | Yes |
| `bingx-spot-wallet` | Wallet: deposit, withdraw, transfer records, etc. | Yes |

### Coin-M Perpetual Futures

| Skill | Purpose | Auth Required |
|-------|---------|---------------|
| `bingx-coinm-market` | Market data: price, depth, klines, funding rate, etc. | No |
| `bingx-coinm-trade` | Trading: place/cancel orders, leverage, margin mode, etc. | Yes |

### Copy Trading

| Skill | Purpose | Auth Required |
|-------|---------|---------------|
| `bingx-copytrade-spot` | Spot copy trading: sell copy positions, query profit, etc. | Yes |
| `bingx-copytrade-swap` | Futures copy trading: close positions, set TP/SL, commission, etc. | Yes |

### Account Management

| Skill | Purpose | Auth Required |
|-------|---------|---------------|
| `bingx-fund-account` | Fund account: balance query, asset overview, inter-account transfers, etc. | Yes |
| `bingx-sub-account` | Sub-account: create/freeze sub-accounts, API key management, etc. | Yes |
| `bingx-agent` | Agent/broker: invited users, commission queries, partner data, etc. | Yes |

### Standard Contract

| Skill | Purpose | Auth Required |
|-------|---------|---------------|
| `bingx-standard-trade` | Standard contract: position query, order history, balance query, etc. | Yes |

---

## Safety Mechanisms

### Write Operation Confirmation

In the `prod-live` (production) environment, all write operations (placing orders, canceling orders, transfers, etc.) require you to type **CONFIRM** before execution. The simulated environment does not require confirmation.

### Key Masking

The AI automatically masks sensitive keys when displaying them:

- API Key: shows first 5 + last 4 characters, e.g. `su1Qc...8akf`
- Secret Key: fully masked, shows only last 5 characters, e.g. `***...aws1`

---

## File Structure

Each skill module consists of two files:

```
skills/<skill-name>/
├── SKILL.md           # Agent behavior instructions
└── api-reference.md   # Complete API documentation
```

Shared reference documents are in the [skills/references/](skills/references/) directory:

- [authentication.md](skills/references/authentication.md) — HMAC SHA256 signing implementation
- [base-urls.md](skills/references/base-urls.md) — Environment base URL configuration

---
