# GMX MCP Server - Quick Usage Guide

## Setup

1. **Install:**
   ```bash
   python setup.py
   ```

2. **Configure:**
   Edit `.env.local` with your wallet details:
   ```
   PRIVATE_KEY=your_private_key_here
   WALLET_ADDRESS=0xYourWalletAddress
   ```

3. **Start:**
   ```bash
   python src/gmx_server.py
   ```

4. **Claude Desktop:**
   Copy `examples/claude_desktop_config.json` to your Claude Desktop MCP config.

## Commands

| Command | Description |
|---------|-------------|
| `setup_wallet()` | Configure wallet (uses .env.local) |
| `get_wallet_info()` | View current config |
| `get_gmx_markets()` | Available markets |
| `estimate_trading_costs("ETH", 1000, True)` | Cost estimation |
| `create_trading_plan("ETH", "long", 1000, 100)` | Trading plan |
| `help_gmx_trading()` | Help |

## Example Usage

```python
# Setup (reads from .env.local)
setup_wallet()

# Get market info
get_gmx_markets()

# Plan a trade
create_trading_plan("ETH", "long", 1000, 100, 2000, 1800, 2200)

# Estimate costs
estimate_trading_costs("ETH", 1000, True, "arbitrum")
```

## Project Structure

- `src/` - Main server code
- `config/` - Configuration templates
- `examples/` - Usage examples
- `docs/` - Documentation
- `.env.local` - Your wallet config (create this)

**Security:** Keep your private key secure. Never commit `.env.local` to git.
