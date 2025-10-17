#!/usr/bin/env python3
"""
Simple test client to demonstrate the FastMCP Name Server functionality.
This script shows how to interact with the MCP server tools.
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test the MCP server tools."""
    
    # Server parameters - adjust the command as needed
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            print("Testing FastMCP Name Server")
            print("=" * 40)
            
            # Test get_name tool
            print("\n1. Testing get_name tool:")
            result = await session.call_tool("get_name", {"name": "Alice"})
            print(f"Input: Alice")
            print(f"Output: {result.content}")
            
            # Test print_name tool
            print("\n2. Testing print_name tool:")
            result = await session.call_tool("print_name", {"name": "Bob"})
            print(f"Input: Bob")
            print(f"Output: {result.content}")
            
            # Test format_name tool with different formats
            print("\n3. Testing format_name tool:")
            
            test_cases = [
                ("john", "uppercase"),
                ("MARY", "lowercase"),
                ("alice smith", "title"),
                ("hello", "reverse")
            ]
            
            for name, format_type in test_cases:
                result = await session.call_tool("format_name", {
                    "name": name,
                    "format_type": format_type
                })
                print(f"Input: {name} ({format_type})")
                print(f"Output: {result.content}")
                print()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
