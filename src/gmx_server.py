#!/usr/bin/env python3
"""
GMX Trading MCP Server
A comprehensive MCP server for GMX v2 trading operations with .env.local support.
"""

import asyncio
import json
import os
import yaml
from typing import Dict, List, Optional, Union
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

# Create the FastMCP server instance
mcp = FastMCP("GMX Trading Server")

# Configuration from environment
config_data = {
    'rpcs': {
        'arbitrum': os.getenv('ARBITRUM_RPC', 'https://arbitrum.meowrpc.com'),
        'avalanche': os.getenv('AVALANCHE_RPC', 'https://api.avax.network/ext/bc/C/rpc')
    },
    'chain_ids': {
        'arbitrum': 42161,
        'avalanche': 43114
    },
    'private_key': os.getenv('PRIVATE_KEY'),
    'user_wallet_address': os.getenv('WALLET_ADDRESS')
}

@mcp.tool()
async def setup_wallet(private_key: str = None, wallet_address: str = None, chain: str = "arbitrum") -> str:
    """
    Set up wallet configuration for GMX trading.
    
    Args:
        private_key: Your wallet's private key (optional if set in .env.local)
        wallet_address: Your wallet address (optional if set in .env.local)
        chain: Blockchain to use (arbitrum or avalanche)
        
    Returns:
        Configuration status message
    """
    global config_data
    
    try:
        # Use provided values or fall back to environment
        if private_key:
            config_data['private_key'] = private_key
        if wallet_address:
            config_data['user_wallet_address'] = wallet_address
            
        if not config_data.get('private_key') or not config_data.get('user_wallet_address'):
            return "Error: Private key and wallet address must be provided either as parameters or in .env.local file"
        
        # Save to file for persistence
        config_path = 'config/gmx_config.yaml'
        os.makedirs('config', exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        
        return f"Wallet configured successfully for {chain}!\nAddress: {config_data['user_wallet_address']}\nChain: {chain.upper()}"
        
    except Exception as e:
        return f"Error setting up wallet: {str(e)}"

@mcp.tool()
async def get_wallet_info() -> str:
    """Get current wallet configuration."""
    global config_data
    
    if not config_data.get('user_wallet_address'):
        return "No wallet configured. Please use setup_wallet() or set WALLET_ADDRESS in .env.local"
    
    return f"""
Current Wallet Configuration:
- Address: {config_data['user_wallet_address']}
- Arbitrum RPC: {config_data['rpcs']['arbitrum']}
- Avalanche RPC: {config_data['rpcs']['avalanche']}
- Private Key: {'***configured***' if config_data.get('private_key') else 'Not set'}

Status: Ready for GMX trading
"""

@mcp.tool()
async def get_gmx_markets() -> str:
    """Get information about available GMX markets."""
    markets_info = {
        "arbitrum": {
            "ETH/USD": {"description": "Ethereum perpetual", "index_token": "ETH", "long_collateral": "ETH", "short_collateral": "USDC"},
            "BTC/USD": {"description": "Bitcoin perpetual", "index_token": "BTC", "long_collateral": "BTC", "short_collateral": "USDC"},
            "ARB/USD": {"description": "Arbitrum perpetual", "index_token": "ARB", "long_collateral": "ARB", "short_collateral": "USDC"},
            "SOL/USD": {"description": "Solana perpetual", "index_token": "SOL", "long_collateral": "SOL", "short_collateral": "USDC"}
        }
    }
    return json.dumps(markets_info, indent=2)

@mcp.tool()
async def estimate_trading_costs(market: str, size_usd: float, is_long: bool = True, chain: str = "arbitrum") -> str:
    """Estimate trading costs and requirements for a position."""
    direction = "LONG" if is_long else "SHORT"
    opening_fee = size_usd * 0.0006
    price_impact = size_usd * 0.0001 if size_usd < 100000 else size_usd * 0.0005
    gas_cost = 15 if chain == "arbitrum" else 2
    
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
            "minimum_collateral_usd": round(size_usd * 0.01, 2),
            "recommended_collateral_usd": round(size_usd * 0.1, 2),
            "max_leverage": "100x",
            "recommended_leverage": "10x"
        }
    }
    return json.dumps(estimate, indent=2)

@mcp.tool()
async def create_trading_plan(market: str, direction: str, size_usd: float, collateral_usd: float, 
                            entry_price: float = None, stop_loss: float = None, take_profit: float = None) -> str:
    """Create a detailed trading plan for a GMX position."""
    is_long = direction.lower() == "long"
    leverage = size_usd / collateral_usd
    
    # Calculate liquidation price
    if entry_price:
        if is_long:
            liquidation_price = entry_price * (1 - (collateral_usd / size_usd) * 0.9)
        else:
            liquidation_price = entry_price * (1 + (collateral_usd / size_usd) * 0.9)
    else:
        liquidation_price = None
    
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
            "1. Ensure sufficient collateral token balance",
            "2. Approve token spending for GMX contracts", 
            "3. Create position order with specified parameters",
            "4. Monitor position and market conditions",
            "5. Execute stop loss or take profit as needed"
        ]
    }
    return json.dumps(plan, indent=2)

@mcp.tool()
async def help_gmx_trading() -> str:
    """Get help information about available GMX trading commands."""
    return """
GMX Trading MCP Server

AVAILABLE COMMANDS:
- setup_wallet(private_key, wallet_address, chain) - Configure wallet
- get_wallet_info() - View current configuration
- get_gmx_markets() - Get available markets
- estimate_trading_costs(market, size_usd, is_long, chain) - Estimate costs
- create_trading_plan(market, direction, size_usd, collateral_usd, ...) - Create trading plan
- help_gmx_trading() - This help

ENVIRONMENT SETUP:
Create .env.local file with:
PRIVATE_KEY=your_private_key_here
WALLET_ADDRESS=0xYourWalletAddress
ARBITRUM_RPC=https://arbitrum.meowrpc.com
AVALANCHE_RPC=https://api.avax.network/ext/bc/C/rpc

EXAMPLE USAGE:
1. setup_wallet() - Uses .env.local values
2. get_gmx_markets()
3. estimate_trading_costs("ETH", 1000, True, "arbitrum")
4. create_trading_plan("ETH", "long", 1000, 100, 2000, 1800, 2200)
"""

def main():
    """Main function to run the GMX MCP server."""
    print("Starting GMX Trading MCP Server...")
    print("Using .env.local for configuration")
    mcp.run()

if __name__ == "__main__":
    main()
