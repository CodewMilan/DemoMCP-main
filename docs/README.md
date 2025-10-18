# GMX Trading MCP Server

A Model Context Protocol (MCP) server for GMX v2 trading operations with Claude Desktop.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install fastmcp python-dotenv pyyaml
   ```

2. **Configure environment:**
   ```bash
   cp config/env.example .env.local
   # Edit .env.local with your wallet details
   ```

3. **Start server:**
   ```bash
   python src/gmx_server.py
   ```

4. **Add to Claude Desktop:**
   Copy `examples/claude_desktop_config.json` to your Claude Desktop MCP config.

## Commands

- `setup_wallet()` - Configure wallet
- `get_wallet_info()` - View configuration  
- `get_gmx_markets()` - Available markets
- `estimate_trading_costs(market, size_usd, is_long, chain)` - Cost estimation
- `create_trading_plan(market, direction, size_usd, collateral_usd, ...)` - Trading plan
- `help_gmx_trading()` - Help

## Security

- Private keys stored in `.env.local` (not committed to git)
- All operations default to debug mode
- Comprehensive risk analysis and warnings

## Example Usage

```python
# Setup (uses .env.local)
setup_wallet()

# Get market info
get_gmx_markets()

# Plan a trade
create_trading_plan("ETH", "long", 1000, 100, 2000, 1800, 2200)
```

**⚠️ Warning:** Trading involves risk. Only trade with money you can afford to lose.
