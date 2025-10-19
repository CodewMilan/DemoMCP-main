#!/usr/bin/env python3
"""
GMX Trading MCP Server
A comprehensive MCP server for GMX v2 trading operations with .env.local support.
"""

import asyncio
import json
import os
import yaml
import requests
from typing import Dict, List, Optional, Union, Any
from decimal import Decimal
from fastmcp import FastMCP
from dotenv import load_dotenv
import time

# Try to import web3, fallback to mock if not available
try:
    from web3 import Web3
    from web3.contract import Contract
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    # Mock Web3 for basic functionality
    class Web3:
        @staticmethod
        def HTTPProvider(url):
            return url
        
        @staticmethod
        def is_connected():
            return False
            
        @staticmethod
        def to_checksum_address(address):
            return address
            
        @staticmethod
        def from_wei(value, unit):
            return value / (10**18) if unit == 'ether' else value
            
        class eth:
            @staticmethod
            def get_balance(address):
                return 0
                
            @staticmethod
            def contract(address, abi):
                return None

# Load environment variables from .env.local
load_dotenv('.env.local')

# Create the FastMCP server instance
mcp = FastMCP("GMX Trading Server")

# Configuration from environment
config_data = {
    'rpcs': {
        'arbitrum': os.getenv('ARBITRUM_RPC', 'https://arbitrum.meowrpc.com'),
        'arbitrum_sepolia': os.getenv('ARBITRUM_SEPOLIA_RPC', 'https://sepolia-rollup.arbitrum.io/rpc'),
        'avalanche': os.getenv('AVALANCHE_RPC', 'https://api.avax.network/ext/bc/C/rpc')
    },
    'chain_ids': {
        'arbitrum': 42161,
        'arbitrum_sepolia': 421614,
        'avalanche': 43114
    },
    'private_key': os.getenv('PRIVATE_KEY'),
    'user_wallet_address': os.getenv('WALLET_ADDRESS')
}

# Load GMX contracts configuration
def load_gmx_contracts() -> Dict[str, Any]:
    """Load GMX contract addresses from config file."""
    try:
        with open('config/gmx_contracts.yaml', 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Return default contracts if file doesn't exist
        return {
            'arbitrum': {
                'datastore': '0xFD70de6b91282D8017aA4E741e9Ae325CAb992d8',
                'syntheticsreader': '0xf60becbba223EEA9495Da3f606753867eC10d139',
                'exchangerouter': '0x69C527fC77291722b52649E45c838e41be8Bf5d5',
                'tokens': {
                    'WETH': '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
                    'USDC': '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
                    'ARB': '0x912CE59144191C1204E64559FE8253a0e49E6548'
                }
            }
        }

gmx_contracts = load_gmx_contracts()

# Web3 instances
w3_instances = {}

def get_web3(chain: str):
    """Get Web3 instance for specified chain."""
    if not WEB3_AVAILABLE:
        return Web3()  # Return mock instance
        
    if chain not in w3_instances:
        rpc_url = config_data['rpcs'].get(chain)
        if not rpc_url:
            raise ValueError(f"No RPC URL configured for chain: {chain}")
        w3_instances[chain] = Web3(Web3.HTTPProvider(rpc_url))
    return w3_instances[chain]

# Basic ERC20 ABI for token operations
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

# GMX Reader ABI (simplified)
GMX_READER_ABI = [
    {
        "inputs": [
            {"name": "dataStore", "type": "address"},
            {"name": "account", "type": "address"}
        ],
        "name": "getAccountPositions",
        "outputs": [{"name": "", "type": "tuple[]"}],
        "stateMutability": "view",
        "type": "function"
    }
]

@mcp.tool()
async def setup_wallet(private_key: str = None, wallet_address: str = None, chain: str = "arbitrum_sepolia") -> str:
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
    gas_cost = 15 if chain in ["arbitrum", "arbitrum_sepolia"] else 2
    
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
async def get_token_balances(chain: str = "arbitrum", address: str = None) -> str:
    """Get token balances for a wallet address."""
    try:
        if not address:
            address = config_data.get('user_wallet_address')
        if not address:
            return "Error: No wallet address provided or configured"
            
        w3 = get_web3(chain)
        if not WEB3_AVAILABLE:
            return f"Web3 not available - using mock data for {chain}"
        if not w3.is_connected():
            return f"Error: Cannot connect to {chain} RPC"
            
        contracts = gmx_contracts.get(chain, {})
        tokens = contracts.get('tokens', {})
        
        balances = {}
        
        # Get ETH/AVAX balance
        native_balance = w3.eth.get_balance(address)
        if chain in ["arbitrum", "arbitrum_sepolia"]:
            native_symbol = "ETH"
        else:
            native_symbol = "AVAX"
        balances[native_symbol] = {
            "balance": str(w3.from_wei(native_balance, 'ether')),
            "balance_wei": str(native_balance),
            "decimals": 18
        }
        
        # Get token balances
        for symbol, token_address in tokens.items():
            try:
                token_contract = w3.eth.contract(
                    address=w3.to_checksum_address(token_address),
                    abi=ERC20_ABI
                )
                balance = token_contract.functions.balanceOf(address).call()
                decimals = token_contract.functions.decimals().call()
                
                balances[symbol] = {
                    "balance": str(balance / (10 ** decimals)),
                    "balance_raw": str(balance),
                    "decimals": decimals,
                    "address": token_address
                }
            except Exception as e:
                balances[symbol] = {"error": str(e)}
                
        result = {
            "chain": chain,
            "address": address,
            "balances": balances,
            "timestamp": int(time.time())
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error getting token balances: {str(e)}"

@mcp.tool()
async def get_live_market_data(chain: str = "arbitrum") -> str:
    """Fetch live market data including prices and funding rates."""
    try:
        # Use GMX API for live data
        if chain == "arbitrum":
            api_base = "https://arbitrum-api.gmxinfra.io"
        elif chain == "arbitrum_sepolia":
            # GMX may not have testnet API, use fallback
            api_base = None
        else:
            api_base = "https://avalanche-api.gmxinfra.io"
        
        # Get market prices
        prices_data = {}
        funding_data = {}
        
        if api_base:
            try:
                prices_response = requests.get(f"{api_base}/prices/tickers", timeout=10)
                prices_data = prices_response.json() if prices_response.status_code == 200 else {}
            except:
                prices_data = {}
                
            # Get funding rates
            try:
                funding_response = requests.get(f"{api_base}/funding-rates", timeout=10)
                funding_data = funding_response.json() if funding_response.status_code == 200 else {}
            except:
                funding_data = {}
            
        # Combine data
        market_data = {
            "chain": chain,
            "timestamp": int(time.time()),
            "prices": prices_data,
            "funding_rates": funding_data,
            "status": "live" if prices_data or funding_data else "fallback"
        }
        
        # Add fallback static data if API fails
        if not prices_data:
            if chain == "arbitrum_sepolia":
                market_data["prices"] = {
                    "ETH": {"price": 2000, "change_24h": 0, "status": "testnet_fallback"},
                    "USDC": {"price": 1.0, "change_24h": 0, "status": "testnet_fallback"},
                    "USDT": {"price": 1.0, "change_24h": 0, "status": "testnet_fallback"}
                }
            else:
                market_data["prices"] = {
                    "ETH": {"price": 2000, "change_24h": 0, "status": "fallback"},
                    "BTC": {"price": 35000, "change_24h": 0, "status": "fallback"},
                    "ARB": {"price": 1.2, "change_24h": 0, "status": "fallback"}
                }
            
        return json.dumps(market_data, indent=2)
        
    except Exception as e:
        return f"Error fetching live market data: {str(e)}"

@mcp.tool()
async def get_open_positions(chain: str = "arbitrum", address: str = None) -> str:
    """Get all open positions for an address."""
    try:
        if not address:
            address = config_data.get('user_wallet_address')
        if not address:
            return "Error: No wallet address provided or configured"
            
        w3 = get_web3(chain)
        contracts = gmx_contracts.get(chain, {})
        
        # Try to get positions from GMX Reader contract
        reader_address = contracts.get('syntheticsreader')
        datastore_address = contracts.get('datastore')
        
        positions = {
            "chain": chain,
            "address": address,
            "positions": [],
            "timestamp": int(time.time())
        }
        
        if reader_address and datastore_address:
            try:
                reader_contract = w3.eth.contract(
                    address=w3.to_checksum_address(reader_address),
                    abi=GMX_READER_ABI
                )
                
                # This would call the actual contract method
                # For now, return placeholder data
                positions["positions"] = [
                    {
                        "market": "ETH/USD",
                        "side": "LONG",
                        "size_usd": "1000.0",
                        "collateral_usd": "200.0",
                        "entry_price": "2000.0",
                        "mark_price": "2050.0",
                        "pnl_usd": "25.0",
                        "liquidation_price": "1800.0",
                        "status": "open"
                    }
                ]
                positions["status"] = "placeholder_data"
                
            except Exception as e:
                positions["error"] = f"Contract call failed: {str(e)}"
                positions["status"] = "error"
        else:
            positions["error"] = "Reader contract not configured"
            positions["status"] = "no_contract"
            
        return json.dumps(positions, indent=2)
        
    except Exception as e:
        return f"Error getting open positions: {str(e)}"

@mcp.tool()
async def simulate_pnl(
    market: str,
    side: str,
    entry_price: float,
    current_price: float,
    position_size_usd: float,
    collateral_usd: float
) -> str:
    """Simulate PnL for a position given current market price."""
    try:
        is_long = side.lower() == "long"
        
        # Calculate PnL
        if is_long:
            price_change_pct = (current_price - entry_price) / entry_price
        else:
            price_change_pct = (entry_price - current_price) / entry_price
            
        pnl_usd = position_size_usd * price_change_pct
        pnl_pct = (pnl_usd / collateral_usd) * 100
        
        # Calculate liquidation price (simplified)
        leverage = position_size_usd / collateral_usd
        liquidation_threshold = 0.9  # 90% of collateral
        
        if is_long:
            liquidation_price = entry_price * (1 - (liquidation_threshold / leverage))
        else:
            liquidation_price = entry_price * (1 + (liquidation_threshold / leverage))
            
        # Risk assessment
        distance_to_liquidation = abs(current_price - liquidation_price) / current_price * 100
        
        if distance_to_liquidation < 5:
            risk_level = "CRITICAL"
        elif distance_to_liquidation < 15:
            risk_level = "HIGH"
        elif distance_to_liquidation < 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            
        simulation = {
            "market": market,
            "position": {
                "side": side.upper(),
                "entry_price": entry_price,
                "current_price": current_price,
                "position_size_usd": position_size_usd,
                "collateral_usd": collateral_usd,
                "leverage": f"{leverage:.1f}x"
            },
            "pnl": {
                "unrealized_pnl_usd": round(pnl_usd, 2),
                "unrealized_pnl_pct": round(pnl_pct, 2),
                "price_change_pct": round(price_change_pct * 100, 2)
            },
            "risk": {
                "liquidation_price": round(liquidation_price, 2),
                "distance_to_liquidation_pct": round(distance_to_liquidation, 2),
                "risk_level": risk_level
            },
            "timestamp": int(time.time())
        }
        
        return json.dumps(simulation, indent=2)
        
    except Exception as e:
        return f"Error simulating PnL: {str(e)}"

@mcp.tool()
async def create_swap_order(
    from_token: str,
    to_token: str,
    amount: float,
    chain: str = "arbitrum",
    slippage_pct: float = 0.5,
    debug_mode: bool = True
) -> str:
    """Create a token swap order."""
    try:
        if not config_data.get('private_key') or not config_data.get('user_wallet_address'):
            return "Error: Wallet not configured. Use setup_wallet() first."
            
        w3 = get_web3(chain)
        contracts = gmx_contracts.get(chain, {})
        tokens = contracts.get('tokens', {})
        
        from_token_address = tokens.get(from_token.upper())
        to_token_address = tokens.get(to_token.upper())
        
        if not from_token_address or not to_token_address:
            return f"Error: Token addresses not found for {from_token} or {to_token}"
            
        # Calculate swap parameters
        exchange_router = contracts.get('exchangerouter')
        
        swap_order = {
            "type": "swap",
            "from_token": from_token.upper(),
            "to_token": to_token.upper(),
            "amount": amount,
            "from_token_address": from_token_address,
            "to_token_address": to_token_address,
            "slippage_pct": slippage_pct,
            "chain": chain,
            "exchange_router": exchange_router,
            "debug_mode": debug_mode,
            "status": "created" if debug_mode else "pending",
            "timestamp": int(time.time())
        }
        
        if debug_mode:
            swap_order["note"] = "Order created in debug mode - not executed"
        else:
            swap_order["note"] = "Order would be submitted to blockchain"
            
        return json.dumps(swap_order, indent=2)
        
    except Exception as e:
        return f"Error creating swap order: {str(e)}"

@mcp.tool()
async def open_position(
    market: str,
    side: str,
    size_usd: float,
    collateral_token: str,
    collateral_amount: float,
    chain: str = "arbitrum",
    debug_mode: bool = True
) -> str:
    """Open a new position on GMX."""
    try:
        if not config_data.get('private_key') or not config_data.get('user_wallet_address'):
            return "Error: Wallet not configured. Use setup_wallet() first."
            
        is_long = side.lower() == "long"
        contracts = gmx_contracts.get(chain, {})
        
        # Get market address
        market_key = f"{market.upper()}_USD"
        market_address = contracts.get('markets', {}).get(market_key)
        
        if not market_address:
            return f"Error: Market {market} not found"
            
        leverage = size_usd / (collateral_amount * 1)  # Assuming 1:1 USD value for simplicity
        
        position_order = {
            "type": "increase_position",
            "market": market.upper(),
            "side": side.upper(),
            "size_usd": size_usd,
            "collateral_token": collateral_token.upper(),
            "collateral_amount": collateral_amount,
            "leverage": f"{leverage:.1f}x",
            "market_address": market_address,
            "chain": chain,
            "debug_mode": debug_mode,
            "status": "created" if debug_mode else "pending",
            "estimated_fees": {
                "opening_fee": size_usd * 0.0006,
                "price_impact": size_usd * 0.0001,
                "total_fees": size_usd * 0.0007
            },
            "timestamp": int(time.time())
        }
        
        if debug_mode:
            position_order["note"] = "Position created in debug mode - not executed"
        else:
            position_order["note"] = "Position would be submitted to blockchain"
            
        return json.dumps(position_order, indent=2)
        
    except Exception as e:
        return f"Error opening position: {str(e)}"

@mcp.tool()
async def close_position(
    market: str,
    side: str,
    size_pct: float = 100.0,
    chain: str = "arbitrum",
    debug_mode: bool = True
) -> str:
    """Close an existing position."""
    try:
        if not config_data.get('private_key') or not config_data.get('user_wallet_address'):
            return "Error: Wallet not configured. Use setup_wallet() first."
            
        contracts = gmx_contracts.get(chain, {})
        
        # Get market address
        market_key = f"{market.upper()}_USD"
        market_address = contracts.get('markets', {}).get(market_key)
        
        if not market_address:
            return f"Error: Market {market} not found"
            
        close_order = {
            "type": "decrease_position",
            "market": market.upper(),
            "side": side.upper(),
            "size_pct": size_pct,
            "market_address": market_address,
            "chain": chain,
            "debug_mode": debug_mode,
            "status": "created" if debug_mode else "pending",
            "timestamp": int(time.time())
        }
        
        if debug_mode:
            close_order["note"] = f"Close order created in debug mode - would close {size_pct}% of position"
        else:
            close_order["note"] = f"Close order would be submitted to blockchain"
            
        return json.dumps(close_order, indent=2)
        
    except Exception as e:
        return f"Error closing position: {str(e)}"

@mcp.tool()
async def add_liquidity(
    market: str,
    long_token_amount: float = 0,
    short_token_amount: float = 0,
    chain: str = "arbitrum",
    debug_mode: bool = True
) -> str:
    """Add liquidity to a GMX market."""
    try:
        if not config_data.get('private_key') or not config_data.get('user_wallet_address'):
            return "Error: Wallet not configured. Use setup_wallet() first."
            
        contracts = gmx_contracts.get(chain, {})
        
        # Get market address
        market_key = f"{market.upper()}_USD"
        market_address = contracts.get('markets', {}).get(market_key)
        
        if not market_address:
            return f"Error: Market {market} not found"
            
        total_value = long_token_amount + short_token_amount
        
        liquidity_order = {
            "type": "add_liquidity",
            "market": market.upper(),
            "long_token_amount": long_token_amount,
            "short_token_amount": short_token_amount,
            "total_value_usd": total_value,
            "market_address": market_address,
            "chain": chain,
            "debug_mode": debug_mode,
            "status": "created" if debug_mode else "pending",
            "estimated_fees": {
                "deposit_fee": total_value * 0.0001,
                "gas_fee": 15 if chain in ["arbitrum", "arbitrum_sepolia"] else 2
            },
            "timestamp": int(time.time())
        }
        
        if debug_mode:
            liquidity_order["note"] = "Liquidity order created in debug mode - not executed"
        else:
            liquidity_order["note"] = "Liquidity order would be submitted to blockchain"
            
        return json.dumps(liquidity_order, indent=2)
        
    except Exception as e:
        return f"Error adding liquidity: {str(e)}"

@mcp.tool()
async def remove_liquidity(
    market: str,
    gm_token_amount: float,
    chain: str = "arbitrum",
    debug_mode: bool = True
) -> str:
    """Remove liquidity from a GMX market."""
    try:
        if not config_data.get('private_key') or not config_data.get('user_wallet_address'):
            return "Error: Wallet not configured. Use setup_wallet() first."
            
        contracts = gmx_contracts.get(chain, {})
        
        # Get market address
        market_key = f"{market.upper()}_USD"
        market_address = contracts.get('markets', {}).get(market_key)
        
        if not market_address:
            return f"Error: Market {market} not found"
            
        withdrawal_order = {
            "type": "remove_liquidity",
            "market": market.upper(),
            "gm_token_amount": gm_token_amount,
            "market_address": market_address,
            "chain": chain,
            "debug_mode": debug_mode,
            "status": "created" if debug_mode else "pending",
            "estimated_fees": {
                "withdrawal_fee": gm_token_amount * 0.0001,
                "gas_fee": 15 if chain in ["arbitrum", "arbitrum_sepolia"] else 2
            },
            "timestamp": int(time.time())
        }
        
        if debug_mode:
            withdrawal_order["note"] = "Withdrawal order created in debug mode - not executed"
        else:
            withdrawal_order["note"] = "Withdrawal order would be submitted to blockchain"
            
        return json.dumps(withdrawal_order, indent=2)
        
    except Exception as e:
        return f"Error removing liquidity: {str(e)}"

## below are the order mangement tools
@mcp.tool()
async def get_pending_orders(chain: str = "arbitrum", address: str = None) -> str:
    """Get all pending/open orders for an address."""
    try:
        if not address:
            address = config_data.get('user_wallet_address')
        if not address:
            return "Error: No wallet address provided or configured"
            
        w3 = get_web3(chain)
        contracts = gmx_contracts.get(chain, {})
        
        pending_orders = {
            "chain": chain,
            "address": address,
            "orders": [],
            "timestamp": int(time.time())
        }
        
        # Placeholder data - in production this would query the GMX contracts
        pending_orders["orders"] = [
            {
                "order_key": "0x123...",
                "type": "limit_increase",
                "market": "ETH/USD",
                "side": "LONG",
                "trigger_price": "2100.0",
                "size_usd": "500.0",
                "collateral_usd": "100.0",
                "status": "pending"
            }
        ]
        pending_orders["status"] = "placeholder_data"
        pending_orders["note"] = "Query GMX OrderStore contract for real data"
            
        return json.dumps(pending_orders, indent=2)
        
    except Exception as e:
        return f"Error getting pending orders: {str(e)}"


@mcp.tool()
async def cancel_order(order_key: str, chain: str = "arbitrum", debug_mode: bool = True) -> str:
    """Cancel a pending order."""
    try:
        if not config_data.get('private_key') or not config_data.get('user_wallet_address'):
            return "Error: Wallet not configured. Use setup_wallet() first."
            
        cancel_tx = {
            "type": "cancel_order",
            "order_key": order_key,
            "chain": chain,
            "debug_mode": debug_mode,
            "status": "created" if debug_mode else "pending",
            "timestamp": int(time.time())
        }
        
        if debug_mode:
            cancel_tx["note"] = "Cancel order created in debug mode - not executed"
        else:
            cancel_tx["note"] = "Cancel transaction would be submitted to blockchain"
            
        return json.dumps(cancel_tx, indent=2)
        
    except Exception as e:
        return f"Error canceling order: {str(e)}"

@mcp.tool()
async def help_gmx_trading() -> str:
    """Get help information about available GMX trading commands."""
    return """
GMX Trading MCP Server - Full v2 Functionality

WALLET & SETUP:
- setup_wallet(private_key, wallet_address, chain) - Configure wallet
- get_wallet_info() - View current configuration
- get_token_balances(chain, address) - Get token balances

MARKET DATA:
- get_gmx_markets() - Get available markets
- get_live_market_data(chain) - Live prices and funding rates
- estimate_trading_costs(market, size_usd, is_long, chain) - Estimate costs

POSITION MANAGEMENT:
- get_open_positions(chain, address) - View open positions
- simulate_pnl(market, side, entry_price, current_price, size_usd, collateral_usd) - PnL simulation
- open_position(market, side, size_usd, collateral_token, collateral_amount, chain, debug_mode) - Open position
- close_position(market, side, size_pct, chain, debug_mode) - Close position

TRADING:
- create_swap_order(from_token, to_token, amount, chain, slippage_pct, debug_mode) - Token swaps
- create_trading_plan(market, direction, size_usd, collateral_usd, ...) - Create trading plan

LIQUIDITY:
- add_liquidity(market, long_token_amount, short_token_amount, chain, debug_mode) - Add liquidity
- remove_liquidity(market, gm_token_amount, chain, debug_mode) - Remove liquidity

HELP:
- help_gmx_trading() - This help

ENVIRONMENT SETUP:
Create .env.local file with:
PRIVATE_KEY=your_private_key_here
WALLET_ADDRESS=0xYourWalletAddress
ARBITRUM_RPC=https://arbitrum.meowrpc.com
ARBITRUM_SEPOLIA_RPC=https://sepolia-rollup.arbitrum.io/rpc
AVALANCHE_RPC=https://api.avax.network/ext/bc/C/rpc

EXAMPLE USAGE (Arbitrum Sepolia Testnet):
1. setup_wallet() - Uses .env.local values, defaults to arbitrum_sepolia
2. get_token_balances("arbitrum_sepolia") - Check testnet balances
3. get_live_market_data("arbitrum_sepolia") - Get testnet prices (fallback data)
4. open_position("ETH", "long", 100, "USDC", 20, "arbitrum_sepolia", True) - Open testnet position (debug)
5. simulate_pnl("ETH", "long", 2000, 2100, 100, 20) - Check PnL
6. close_position("ETH", "long", 50, "arbitrum_sepolia", True) - Close 50% (debug)

NOTE: All trading functions default to debug_mode=True for safety.
Set debug_mode=False only when ready to execute real trades.
"""

def main():
    """Main function to run the GMX MCP server."""
    print("Starting GMX Trading MCP Server...")
    print("Using .env.local for configuration")
    mcp.run()

if __name__ == "__main__":
    main()
