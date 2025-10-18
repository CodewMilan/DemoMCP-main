#!/usr/bin/env python3
"""
GMX Trading MCP Server - Simplified Version
A simplified MCP server for GMX v2 trading operations that works without complex dependencies.
This version provides essential trading functionality through direct API calls.
"""

import asyncio
import json
import os
import yaml
from typing import Dict, List, Optional, Union
from fastmcp import FastMCP

# Create the FastMCP server instance
mcp = FastMCP("GMX Trading Server - Simple")

# Configuration storage
config_data = {
    'rpcs': {
        'arbitrum': 'https://arbitrum.meowrpc.com',
        'avalanche': 'https://api.avax.network/ext/bc/C/rpc'
    },
    'chain_ids': {
        'arbitrum': 42161,
        'avalanche': 43114
    },
    'private_key': None,
    'user_wallet_address': "0xb6ad1ad1637aD0F5C8DD7BE68876f508E7E368F9"
}

@mcp.tool()
async def setup_wallet(private_key: str, wallet_address: str, chain: str = "arbitrum") -> str:
    """
    Set up wallet configuration for GMX trading.
    
    Args:
        private_key: Your wallet's private key (keep secure!)
        wallet_address: Your wallet address
        chain: Blockchain to use (arbitrum or avalanche)
        
    Returns:
        Configuration status message
    """
    global config_data
    
    try:
        # Update configuration
        config_data['private_key'] = private_key
        config_data['user_wallet_address'] = wallet_address
        
        # Save to file
        config_path = 'gmx_config_simple.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        
        return f"Wallet configured successfully for {chain}!\nAddress: {wallet_address}\nChain: {chain.upper()}\n\nNOTE: This is a simplified version. For full trading functionality, please install the complete GMX Python SDK."
        
    except Exception as e:
        return f"Error setting up wallet: {str(e)}"

@mcp.tool()
async def get_wallet_info() -> str:
    """
    Get current wallet configuration.
    
    Returns:
        Current wallet information
    """
    global config_data
    
    if not config_data.get('user_wallet_address'):
        return "No wallet configured. Please use setup_wallet first."
    
    return f"""
Current Wallet Configuration:
- Address: {config_data['user_wallet_address']}
- Arbitrum RPC: {config_data['rpcs']['arbitrum']}
- Avalanche RPC: {config_data['rpcs']['avalanche']}

Status: Ready for GMX trading (simplified mode)
"""

@mcp.tool()
async def get_gmx_markets() -> str:
    """
    Get information about available GMX markets.
    
    Returns:
        Information about GMX markets
    """
    markets_info = {
        "arbitrum": {
            "ETH/USD": {
                "description": "Ethereum perpetual market",
                "index_token": "ETH",
                "long_collateral": "ETH",
                "short_collateral": "USDC"
            },
            "BTC/USD": {
                "description": "Bitcoin perpetual market", 
                "index_token": "BTC",
                "long_collateral": "BTC",
                "short_collateral": "USDC"
            },
            "ARB/USD": {
                "description": "Arbitrum perpetual market",
                "index_token": "ARB", 
                "long_collateral": "ARB",
                "short_collateral": "USDC"
            },
            "SOL/USD": {
                "description": "Solana perpetual market",
                "index_token": "SOL",
                "long_collateral": "SOL", 
                "short_collateral": "USDC"
            }
        }
    }
    
    return json.dumps(markets_info, indent=2)

@mcp.tool()
async def estimate_trading_costs(
    market: str,
    size_usd: float,
    is_long: bool = True,
    chain: str = "arbitrum"
) -> str:
    """
    Estimate trading costs and requirements for a position.
    
    Args:
        market: Market symbol (e.g., "ETH", "BTC")
        size_usd: Position size in USD
        is_long: True for long position, False for short
        chain: Blockchain to use
        
    Returns:
        Estimated trading costs and requirements
    """
    
    # Simplified cost estimation
    direction = "LONG" if is_long else "SHORT"
    
    # Rough estimates based on typical GMX fees
    opening_fee = size_usd * 0.0006  # 0.06% opening fee
    price_impact = size_usd * 0.0001 if size_usd < 100000 else size_usd * 0.0005  # Estimated price impact
    gas_cost = 15 if chain == "arbitrum" else 2  # Estimated gas cost in USD
    
    min_collateral = size_usd * 0.01  # 1% minimum collateral for 100x leverage
    recommended_collateral = size_usd * 0.1  # 10% recommended collateral for 10x leverage
    
    estimate = {
        "market": f"{market}/USD",
        "direction": direction,
        "position_size_usd": size_usd,
        "chain": chain,
        "estimated_costs": {
            "opening_fee_usd": round(opening_fee, 2),
            "estimated_price_impact_usd": round(price_impact, 2),
            "estimated_gas_cost_usd": round(gas_cost, 2),
            "total_estimated_cost_usd": round(opening_fee + price_impact + gas_cost, 2)
        },
        "collateral_requirements": {
            "minimum_collateral_usd": round(min_collateral, 2),
            "recommended_collateral_usd": round(recommended_collateral, 2),
            "max_leverage": "100x",
            "recommended_leverage": "10x"
        },
        "note": "These are rough estimates. Actual costs may vary based on market conditions."
    }
    
    return json.dumps(estimate, indent=2)

@mcp.tool()
async def create_trading_plan(
    market: str,
    direction: str,
    size_usd: float,
    collateral_usd: float,
    entry_price: float = None,
    stop_loss: float = None,
    take_profit: float = None
) -> str:
    """
    Create a detailed trading plan for a GMX position.
    
    Args:
        market: Market symbol (e.g., "ETH", "BTC")
        direction: "long" or "short"
        size_usd: Position size in USD
        collateral_usd: Collateral amount in USD
        entry_price: Target entry price (optional)
        stop_loss: Stop loss price (optional)
        take_profit: Take profit price (optional)
        
    Returns:
        Detailed trading plan
    """
    
    is_long = direction.lower() == "long"
    leverage = size_usd / collateral_usd
    
    # Calculate liquidation price (simplified)
    if is_long:
        # For long positions, liquidation occurs when price drops
        liquidation_price = entry_price * (1 - (collateral_usd / size_usd) * 0.9) if entry_price else None
    else:
        # For short positions, liquidation occurs when price rises
        liquidation_price = entry_price * (1 + (collateral_usd / size_usd) * 0.9) if entry_price else None
    
    plan = {
        "trading_plan": {
            "market": f"{market}/USD",
            "direction": direction.upper(),
            "position_size_usd": size_usd,
            "collateral_usd": collateral_usd,
            "leverage": f"{leverage:.1f}x",
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "estimated_liquidation_price": round(liquidation_price, 2) if liquidation_price else None
        },
        "risk_analysis": {
            "leverage_risk": "HIGH" if leverage > 20 else "MEDIUM" if leverage > 10 else "LOW",
            "position_size_risk": "HIGH" if size_usd > 50000 else "MEDIUM" if size_usd > 10000 else "LOW",
            "collateral_ratio": f"{(collateral_usd/size_usd)*100:.1f}%"
        },
        "execution_steps": [
            "1. Ensure sufficient collateral token balance in wallet",
            "2. Approve token spending for GMX contracts",
            "3. Create increase position order with specified parameters",
            "4. Monitor position and market conditions",
            "5. Execute stop loss or take profit as needed"
        ],
        "warnings": [
            "High leverage increases liquidation risk",
            "Always monitor positions actively",
            "Consider market volatility and funding rates",
            "Have exit strategy planned before entering"
        ]
    }
    
    return json.dumps(plan, indent=2)

@mcp.tool()
async def get_trading_tutorial() -> str:
    """
    Get a comprehensive tutorial on GMX trading.
    
    Returns:
        Trading tutorial and best practices
    """
    
    tutorial = """
# GMX Trading Tutorial

## What is GMX?
GMX is a decentralized perpetual exchange that allows you to trade cryptocurrencies with leverage up to 100x. It operates on Arbitrum and Avalanche networks.

## Key Concepts

### 1. Perpetual Trading
- Trade without expiration dates
- Use leverage to amplify positions
- Long (bet price goes up) or Short (bet price goes down)

### 2. Collateral
- Deposit tokens to back your position
- Higher collateral = lower liquidation risk
- Can use the same token you're trading or stablecoins

### 3. Leverage
- Multiply your position size
- 10x leverage means $100 collateral controls $1000 position
- Higher leverage = higher risk and potential rewards

## Trading Process

### Step 1: Setup
1. Connect wallet (MetaMask recommended)
2. Ensure you have tokens on Arbitrum or Avalanche
3. Have some ETH/AVAX for gas fees

### Step 2: Choose Position
1. Select market (ETH, BTC, ARB, etc.)
2. Decide direction (Long/Short)
3. Set position size and leverage

### Step 3: Manage Risk
1. Set stop losses to limit downside
2. Consider take profit levels
3. Monitor liquidation price
4. Watch funding rates

### Step 4: Execute
1. Approve token spending
2. Create position order
3. Monitor and manage position
4. Close when targets hit

## Risk Management

### Position Sizing
- Never risk more than you can afford to lose
- Start with small positions to learn
- Recommended: Risk 1-2% of portfolio per trade

### Leverage Guidelines
- Beginners: 2-5x leverage maximum
- Experienced: 10x leverage with tight stops
- Experts only: 20x+ leverage

### Stop Losses
- Always set stop losses
- Risk/reward ratio of at least 1:2
- Move stops to breakeven when profitable

## Common Mistakes to Avoid

1. **Over-leveraging**: Using too much leverage
2. **No stop losses**: Not protecting downside
3. **FOMO trading**: Chasing pumps/dumps
4. **Ignoring funding**: Not considering funding costs
5. **Poor timing**: Not understanding market conditions

## Advanced Features

### Funding Rates
- Long/short imbalance creates funding
- Paid every hour between traders
- Can be positive or negative

### Price Impact
- Large orders can move market price
- More impact in smaller markets
- Consider breaking large orders into smaller ones

## Getting Started Safely

1. **Paper Trade First**: Practice with small amounts
2. **Understand Liquidation**: Know your liquidation price
3. **Start Conservative**: Use low leverage initially
4. **Learn Gradually**: Increase complexity over time
5. **Risk Management**: Never risk more than you can lose

## Useful Commands

- `estimate_trading_costs()`: Calculate fees and requirements
- `create_trading_plan()`: Plan your trade in detail
- `setup_wallet()`: Configure your trading wallet

Remember: Trading is risky. Only trade with money you can afford to lose!
"""
    
    return tutorial

@mcp.tool()
async def help_gmx_trading() -> str:
    """
    Get help information about available GMX trading commands.
    
    Returns:
        Help text with available commands and usage
    """
    help_text = """
GMX Trading MCP Server - Simplified Version

AVAILABLE COMMANDS:

SETUP & CONFIGURATION:
- setup_wallet(private_key, wallet_address, chain) - Configure your wallet
- get_wallet_info() - View current wallet configuration

MARKET INFORMATION:
- get_gmx_markets() - Get available GMX markets
- estimate_trading_costs(market, size_usd, is_long, chain) - Estimate trading costs
- create_trading_plan(market, direction, size_usd, collateral_usd, entry_price, stop_loss, take_profit) - Create detailed trading plan

EDUCATION:
- get_trading_tutorial() - Comprehensive GMX trading tutorial
- help_gmx_trading() - This help message

EXAMPLE USAGE:

1. Setup:
   setup_wallet("your_private_key", "0xYourAddress", "arbitrum")

2. Get market info:
   get_gmx_markets()

3. Estimate costs:
   estimate_trading_costs("ETH", 1000, True, "arbitrum")

4. Plan trade:
   create_trading_plan("ETH", "long", 1000, 100, 2000, 1800, 2200)

5. Learn:
   get_trading_tutorial()

IMPORTANT NOTES:
- This is a simplified version for planning and education
- For actual trading, install the full GMX Python SDK
- Always practice risk management
- Start with small positions
- Never invest more than you can afford to lose

SAFETY REMINDERS:
- Keep your private key secure
- Test with small amounts first
- Understand liquidation risks
- Monitor positions actively
- Have exit strategies planned
"""
    return help_text

def main():
    """Main function to run the simplified GMX MCP server."""
    print("Starting GMX Trading MCP Server (Simplified Version)...")
    print("This version provides planning and educational tools for GMX trading")
    print("For full trading functionality, install the complete GMX Python SDK")
    print("Use help_gmx_trading() to see all available commands")
    
    # Run the server
    mcp.run()

if __name__ == "__main__":
    main()
