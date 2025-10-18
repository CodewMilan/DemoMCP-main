#!/usr/bin/env python3
"""
Test client for GMX MCP Server
Tests the functionality of the GMX trading MCP server.
"""

import asyncio
import json
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

async def test_gmx_server():
    """Test the GMX MCP server functionality"""
    
    print("Testing GMX MCP Server")
    print("=" * 40)
    
    # Import the server functions for testing
    try:
        from gmx_server import (
            help_gmx_trading,
            get_market_data,
            get_oracle_prices,
            estimate_swap_output,
            get_gmx_stats
        )
        print("Successfully imported GMX server functions")
    except ImportError as e:
        print(f"Error importing GMX server: {e}")
        return False
    
    # Test 1: Help function
    print("\nTest 1: Help Function")
    try:
        help_result = await help_gmx_trading()
        print("Help function works")
        print("Help content preview:")
        print(help_result[:200] + "..." if len(help_result) > 200 else help_result)
    except Exception as e:
        print(f"Help function failed: {e}")
    
    # Test 2: Market Data (read-only, safe to test)
    print("\nTest 2: Market Data")
    try:
        market_data = await get_market_data("arbitrum")
        print("Market data retrieval works")
        
        # Parse and display sample data
        if market_data.startswith('{'):
            data = json.loads(market_data)
            print(f"Found {len(data)} markets")
            
            # Show first few markets
            count = 0
            for market_key, market_info in data.items():
                if count < 3:
                    print(f"  - {market_info.get('index_token', 'Unknown')}: {market_key[:10]}...")
                    count += 1
        else:
            print(f"Market data: {market_data[:100]}...")
            
    except Exception as e:
        print(f"Market data test failed: {e}")
    
    # Test 3: Oracle Prices (read-only, safe to test)
    print("\nTest 3: Oracle Prices")
    try:
        prices = await get_oracle_prices("arbitrum")
        print("Oracle prices retrieval works")
        
        if prices.startswith('{'):
            price_data = json.loads(prices)
            print(f"Found prices for {len(price_data)} tokens")
            
            # Show sample prices
            count = 0
            for token, price_info in price_data.items():
                if count < 3 and isinstance(price_info, dict):
                    symbol = price_info.get('symbol', token[:6])
                    price = price_info.get('price', 'N/A')
                    print(f"  - {symbol}: ${price}")
                    count += 1
        else:
            print(f"Price data: {prices[:100]}...")
            
    except Exception as e:
        print(f"Oracle prices test failed: {e}")
    
    # Test 4: Swap Estimation (read-only, safe to test)
    print("\nTest 4: Swap Estimation")
    try:
        swap_estimate = await estimate_swap_output("USDC", "ETH", 1000, "arbitrum")
        print("Swap estimation works")
        
        if swap_estimate.startswith('{'):
            estimate_data = json.loads(swap_estimate)
            print("Swap estimation result:")
            for key, value in estimate_data.items():
                print(f"  - {key}: {value}")
        else:
            print(f"Estimate: {swap_estimate[:100]}...")
            
    except Exception as e:
        print(f"Swap estimation test failed: {e}")
    
    # Test 5: GMX Stats (read-only, safe to test)
    print("\nTest 5: GMX Statistics")
    try:
        stats = await get_gmx_stats("arbitrum")
        print("GMX statistics retrieval works")
        
        if stats.startswith('{'):
            stats_data = json.loads(stats)
            print("Available statistics:")
            for category in stats_data.keys():
                print(f"  - {category}")
        else:
            print(f"Stats: {stats[:100]}...")
            
    except Exception as e:
        print(f"GMX statistics test failed: {e}")
    
    print("\n" + "=" * 40)
    print("GMX MCP Server Testing Complete!")
    print("=" * 40)
    
    print("\nNEXT STEPS:")
    print("1. Start the MCP server: python gmx_server.py")
    print("2. Configure Claude Desktop with the MCP server")
    print("3. Set up your wallet: setup_wallet(private_key, address)")
    print("4. Test with: help_gmx_trading()")
    
    print("\nSAFETY REMINDERS:")
    print("- All trading functions default to debug_mode=True")
    print("- Test with small amounts first")
    print("- Never share your private key")
    print("- Double-check all parameters before executing trades")
    
    return True

def test_configuration():
    """Test configuration files and setup"""
    
    print("\nTesting Configuration")
    print("-" * 30)
    
    # Check if GMX SDK directory exists
    gmx_sdk_path = os.path.join(current_dir, 'gmx_python_sdk-main')
    if os.path.exists(gmx_sdk_path):
        print("GMX SDK directory found")
        
        # Check config file
        config_path = os.path.join(gmx_sdk_path, 'config.yaml')
        if os.path.exists(config_path):
            print("GMX config file found")
        else:
            print("GMX config file not found - will be created on first run")
    else:
        print("GMX SDK directory not found")
        print("   Please ensure gmx_python_sdk-main is in the current directory")
        return False
    
    # Check requirements
    requirements_path = os.path.join(current_dir, 'requirements.txt')
    if os.path.exists(requirements_path):
        print("Requirements file found")
    else:
        print("Requirements file not found")
        return False
    
    # Check main server file
    server_path = os.path.join(current_dir, 'gmx_server.py')
    if os.path.exists(server_path):
        print("GMX server file found")
    else:
        print("GMX server file not found")
        return False
    
    return True

def main():
    """Main test function"""
    
    print("GMX MCP Server Test Suite")
    print("=" * 50)
    
    # Test configuration first
    if not test_configuration():
        print("\nConfiguration test failed. Please run setup_gmx.py first.")
        return
    
    # Run async tests
    try:
        asyncio.run(test_gmx_server())
    except Exception as e:
        print(f"\nTest suite failed: {e}")
        print("Try running: python setup_gmx.py")

if __name__ == "__main__":
    main()
