# BingX OpenAPI Skills for Claude Code

This plugin provides BingX perpetual contract trading skills for Claude Code.

## Skills Included

- **bingx-swap-market** — Market data queries (price, depth, K-lines, funding rate, etc.)
- **bingx-swap-trade** — Trading operations (place orders, cancel orders, leverage settings, etc.)
- **bingx-swap-account** — Account management (balance, positions, commission rates, etc.)

## Installation

### Using npx skills add

```bash
npx skills add BingX-API/api-ai-skills
```

### Using Claude Code /plugin command

In Claude Code conversation:

```
/plugin add BingX-API/api-ai-skills
```

## Prerequisites

You need BingX API credentials:

- **API Key**
- **Secret Key**

Set them as environment variables:

```bash
BINGX_API_KEY="your-api-key"
BINGX_SECRET_KEY="your-secret-key"
```

**Security warning**: Never commit credentials to git (add `.env` to `.gitignore`) and never expose credentials in logs, screenshots, or chat messages.

## Usage Examples

After installation, you can use natural language to interact with BingX:

```
Query BTC-USDT current price
```

```
Place a limit buy order for BTC-USDT at 50000, quantity 0.01
```

```
Show my current positions
```

## License

MIT
