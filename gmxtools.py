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


def main():
    """Main function to run the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()
