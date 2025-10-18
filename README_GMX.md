# GMX Trading MCP Server

A comprehensive Model Context Protocol (MCP) server for GMX v2 trading operations, designed to work seamlessly with Claude Desktop and other MCP-compatible AI assistants.

## 🚀 Features

### Trading Operations
- **Position Management**: Open, increase, decrease, and close positions
- **Token Swaps**: Execute token swaps with slippage protection
- **Liquidity Operations**: Deposit and withdraw from GM pools
- **Portfolio Management**: View and manage all open positions

### Market Data & Analytics
- **Real-time Prices**: Get current oracle prices for all tokens
- **Market Information**: Access comprehensive market data
- **Statistics**: Protocol-wide statistics and metrics
- **Swap Estimation**: Estimate swap outputs and price impact

### Safety Features
- **Debug Mode**: Test all operations without executing real trades
- **Slippage Protection**: Configurable slippage tolerance
- **Wallet Integration**: Secure wallet configuration and management

## 📋 Prerequisites

- Python 3.10 or higher
- Claude Desktop (for MCP integration)
- MetaMask or compatible wallet
- Arbitrum or Avalanche network access

## 🔧 Installation

### 1. Quick Setup (Recommended)

Run the automated setup script:

```bash
python setup_gmx.py
```

This will:
- Install all required dependencies
- Configure the GMX Python SDK
- Set up MCP configuration for Claude Desktop
- Create necessary configuration files

### 2. Manual Setup

If you prefer manual installation:

```bash
# Install dependencies
pip install -r requirements.txt

# Create GMX SDK config
cp gmx_python_sdk-main/config.yaml.example gmx_python_sdk-main/config.yaml

# Edit the config file with your settings
nano gmx_python_sdk-main/config.yaml
```

### 3. Claude Desktop Configuration

Add this to your Claude Desktop MCP configuration (`~/.config/claude-desktop/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gmx-trading": {
      "command": "python",
      "args": ["/path/to/your/gmx_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/your/project"
      }
    }
  }
}
```

## 🔐 Wallet Configuration

### Setting Up Your Wallet

1. **Get Your Private Key**: Export your private key from MetaMask
2. **Configure the Server**: Use the setup command in Claude:

```
setup_wallet("your_private_key_here", "0xYourWalletAddress", "arbitrum")
```

### Security Best Practices

⚠️ **IMPORTANT SECURITY NOTES**:
- Never share your private key
- Use a dedicated trading wallet with limited funds
- Always test with small amounts first
- Keep your private key in a secure location

## 📊 Available Commands

### Setup & Configuration
```
setup_wallet(private_key, wallet_address, chain)
get_wallet_positions(address, chain)
get_market_data(chain)
get_oracle_prices(chain)
```

### Market Data
```
estimate_swap_output(in_token, out_token, amount, chain)
get_gmx_stats(chain)
```

### Trading Operations
```
create_swap_order(start_token, out_token, amount, slippage, chain, debug_mode)
create_increase_position_order(index_token, collateral_token, start_token, is_long, size_usd, leverage, slippage, chain, debug_mode)
close_position(market_symbol, is_long, amount_to_close, collateral_to_remove, out_token, slippage, chain, debug_mode)
```

### Liquidity Operations
```
create_deposit_order(market_token, long_token, short_token, long_usd, short_usd, chain, debug_mode)
```

### Help
```
help_gmx_trading()
```

## 💡 Usage Examples

### 1. Basic Setup and Market Data

```
# Configure your wallet
setup_wallet("your_private_key", "0xYourAddress", "arbitrum")

# Check available markets
get_market_data("arbitrum")

# Get current prices
get_oracle_prices("arbitrum")

# View your positions
get_wallet_positions()
```

### 2. Token Swaps

```
# Estimate swap output
estimate_swap_output("USDC", "ETH", 1000, "arbitrum")

# Execute a swap (debug mode)
create_swap_order("USDC", "ETH", 1000, 0.5, "arbitrum", True)

# Execute actual swap (remove debug mode)
create_swap_order("USDC", "ETH", 1000, 0.5, "arbitrum", False)
```

### 3. Position Trading

```
# Open a long ETH position with 2x leverage
create_increase_position_order("ETH", "USDC", "USDC", True, 2000, 2.0, 0.5, "arbitrum", True)

# Open a short position
create_increase_position_order("BTC", "USDC", "USDC", False, 1000, 3.0, 0.5, "arbitrum", True)

# Close 50% of a position
close_position("ETH", True, 0.5, 0.5, "USDC", 0.5, "arbitrum", True)

# Close entire position
close_position("ETH", True, 1.0, 1.0, "USDC", 0.5, "arbitrum", True)
```

### 4. Liquidity Provision

```
# Deposit liquidity to ETH/USDC pool
create_deposit_order("ETH", "ETH", "USDC", 1000, 1000, "arbitrum", True)
```

## 🛡️ Safety Features

### Debug Mode
All trading operations default to `debug_mode=True`, which:
- Creates and validates orders without executing them
- Allows you to test parameters safely
- Shows what would happen without risking funds

### Slippage Protection
- Configurable slippage tolerance for all operations
- Default 0.5% slippage protection
- Prevents excessive price impact

### Error Handling
- Comprehensive error messages
- Validation of all parameters
- Safe fallbacks for network issues

## 🌐 Supported Networks

### Arbitrum (Recommended)
- Fully tested and supported
- Lower gas fees
- High liquidity

### Avalanche (Experimental)
- Basic support available
- Limited testing
- Use with caution

## 🔧 Configuration Files

### GMX SDK Configuration
Location: `gmx_python_sdk-main/config.yaml`

```yaml
rpcs:
  arbitrum: https://arbitrum.meowrpc.com
  avalanche: https://api.avax.network/ext/bc/C/rpc
chain_ids:
  arbitrum: 42161
  avalanche: 43114
private_key: your_private_key_here
user_wallet_address: your_wallet_address_here
```

### MCP Configuration
Location: `~/.config/claude-desktop/claude_desktop_config.json`

## 🐛 Troubleshooting

### Common Issues

1. **"No wallet configured" error**
   - Run `setup_wallet()` with your credentials
   - Check that config.yaml has correct wallet address

2. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check that gmx_python_sdk-main directory exists

3. **Network connection issues**
   - Verify RPC endpoints in config.yaml
   - Check internet connection
   - Try alternative RPC providers

4. **Transaction failures**
   - Ensure sufficient balance for gas fees
   - Check slippage tolerance
   - Verify token approvals

### Debug Mode Testing

Always test new operations in debug mode first:

```
# Test mode (safe)
create_swap_order("USDC", "ETH", 100, 0.5, "arbitrum", True)

# Live mode (executes real transaction)
create_swap_order("USDC", "ETH", 100, 0.5, "arbitrum", False)
```

## 📚 Additional Resources

- [GMX Protocol Documentation](https://docs.gmx.io/)
- [GMX Python SDK Repository](https://github.com/snipermonke01/gmx_python_sdk)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Claude Desktop MCP Guide](https://claude.ai/mcp)

## ⚖️ License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is provided for educational and research purposes only. Trading cryptocurrencies involves substantial risk of loss. The authors are not responsible for any financial losses incurred through the use of this software. Always do your own research and never invest more than you can afford to lose.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review the GMX SDK documentation

---

**Happy Trading! 🚀**
