#!/usr/bin/env python3
"""
FastMCP Server for GMX Tokens and Signed Prices
Fetches all tokens and the latest signed price data from GMX's public REST APIs without authentication.
"""
import aiohttp
from fastmcp import FastMCP
from typing import Dict, Any

# Create the FastMCP server instance
mcp = FastMCP("GMX Token & Prices Server")

# Base URLs for different chains
ARBITRUM_API = "https://arbitrum-api.gmxinfra.io"
AVALANCHE_API = "https://avalanche-api.gmxinfra.io"


@mcp.tool()
async def ping_gmx(chain: str = "arbitrum") -> Dict[str, Any]:
    """
    Pings the GMX API to check if the server is online.

    Args:
        chain: The blockchain to ping (arbitrum or avalanche)

    Returns:
        Dictionary indicating whether the API is reachable and responsive
    """
    base_url = ARBITRUM_API if chain.lower() == "arbitrum" else AVALANCHE_API
    url = f"{base_url}/ping"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "chain": chain,
                    "status": "online" if data.get("message") == "ok" else "unexpected response",
                    "raw_response": data
                }
            else:
                return {
                    "chain": chain,
                    "status": "offline",
                    "error": f"Failed to ping GMX API (HTTP {response.status})"
                }

@mcp.tool()
async def get_tokens(chain: str = "arbitrum") -> Dict[str, Any]:
    """
    Fetches all available tokens from GMX.
    
    Args:
        chain: The blockchain to fetch from (arbitrum or avalanche)
        
    Returns:
        Dictionary containing token information
    """
    base_url = ARBITRUM_API if chain.lower() == "arbitrum" else AVALANCHE_API
    url = f"{base_url}/tokens"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "chain": chain,
                    "token_count": len(data.get("tokens", [])),
                    "tokens": data.get("tokens", [])
                }
            else:
                return {
                    "error": f"Failed to fetch tokens: {response.status}",
                    "chain": chain
                }   
            

@mcp.tool()
async def get_signed_prices(chain: str = "arbitrum") -> Dict[str, Any]:
    """
    Fetches the latest signed price information from GMX.
    
    Args:
        chain: The blockchain to fetch from (arbitrum or avalanche)
        
    Returns:
        Dictionary containing signed prices
    """
    base_url = ARBITRUM_API if chain.lower() == "arbitrum" else AVALANCHE_API
    url = f"{base_url}/signed_prices/latest"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "chain": chain,
                    "signed_prices_count": len(data.get("signedPrices", [])),
                    "signed_prices": data.get("signedPrices", [])
                }
            else:
                return {
                    "error": f"Failed to fetch signed prices: {response.status}",
                    "chain": chain
                }


@mcp.tool()
async def get_price_tickers(chain: str = "arbitrum") -> Dict[str, Any]:
    """
    Fetches the latest token price tickers from GMX.

    Args:
        chain: The blockchain to fetch from (arbitrum or avalanche)

    Returns:
        Dictionary containing token price ticker information
    """
    base_url = ARBITRUM_API if chain.lower() == "arbitrum" else AVALANCHE_API
    url = f"{base_url}/prices/tickers"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "chain": chain,
                    "ticker_count": len(data),
                    "tickers": [
                        {
                            "symbol": item.get("tokenSymbol"),
                            "address": item.get("tokenAddress"),
                            "min_price": item.get("minPrice"),
                            "max_price": item.get("maxPrice"),
                            "timestamp": item.get("timestamp"),
                        }
                        for item in data
                    ]
                }
            else:
                return {
                    "chain": chain,
                    "error": f"Failed to fetch price tickers (HTTP {response.status})"
                }
            
@mcp.tool()
async def get_price_candles(token_symbol: str = "ETH", period: str = "1d", chain: str = "arbitrum") -> dict:
    """
    Fetches historical candlestick (OHLC) data for a specific token and period.

    Args:
        token_symbol: Symbol of the token (e.g., ETH, BTC)
        period: Time period for each candle (e.g., 1d, 1h)
        chain: The blockchain to fetch from (arbitrum or avalanche)

    Returns:
        Dictionary containing period and a list of candles with timestamp, open, high, low, close prices
    """
    base_url = ARBITRUM_API if chain.lower() == "arbitrum" else AVALANCHE_API
    url = f"{base_url}/prices/candles?tokenSymbol={token_symbol}&period={period}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                candles = [
                    {
                        "timestamp": candle[0],
                        "open": candle[1],
                        "high": candle[2],
                        "low": candle[3],
                        "close": candle[4]
                    }
                    for candle in data.get("candles", [])
                ]
                return {
                    "chain": chain,
                    "token": token_symbol,
                    "period": data.get("period", period),
                    "candle_count": len(candles),
                    "candles": candles
                }
            else:
                return {
                    "chain": chain,
                    "token": token_symbol,
                    "error": f"Failed to fetch candles (HTTP {response.status})"
                }



def main():
    """Main function to run the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()
