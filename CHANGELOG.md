# Changelog

## [0.1.0] - 2026-03-09

### Initial Release

First release of BingX OpenAPI Skills, providing complete BingX Exchange API support for AI coding assistants.

**Core Features:**

- **15 Skill Modules** covering full business scenarios:
  - USDT-M Perpetual Contracts (market, trading, account)
  - Spot Trading (market, trading, account, wallet)
  - Coin-M Perpetual Contracts (market, trading)
  - Copy Trading (spot, contracts)
  - Account Management (fund account, sub-account, agent)

- **Multi-Platform Support**:
  - Supports Claude Code, Cursor, and other mainstream AI assistants
  - Install via `npx skills add` or Claude Code Plugin

- **Security & Ease of Use**:
  - HMAC SHA256 authentication
  - User confirmation required for write operations in production
  - Natural language interaction, no coding required

- **Auto-Update Mechanism** (Claude Code exclusive):
  - Automatically checks for updates on session start
  - Silent background downloads of new versions
