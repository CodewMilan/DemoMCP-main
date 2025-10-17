#!/usr/bin/env python3
"""
FastMCP Server for Name Input/Output
A simple MCP server that takes a name as input and prints it as output.
"""

import asyncio
from fastmcp import FastMCP

# Create the FastMCP server instance
mcp = FastMCP("Name Server")

@mcp.tool()
async def get_name(name: str) -> str:
    """
    Takes a name as input and returns a greeting message with the name.
    
    Args:
        name: The name to process
        
    Returns:
        A greeting message with the provided name
    """
    return f"Hello, {name}! Nice to meet you."

@mcp.tool()
async def print_name(name: str) -> str:
    """
    Takes a name as input and prints it as output.
    
    Args:
        name: The name to print
        
    Returns:
        A confirmation message
    """
    print(f"Name received: {name}")
    return f"Successfully printed: {name}"

@mcp.tool()
async def format_name(name: str, format_type: str = "uppercase") -> str:
    """
    Takes a name and formats it according to the specified format type.
    
    Args:
        name: The name to format
        format_type: The format type (uppercase, lowercase, title, reverse)
        
    Returns:
        The formatted name
    """
    if format_type == "uppercase":
        return name.upper()
    elif format_type == "lowercase":
        return name.lower()
    elif format_type == "title":
        return name.title()
    elif format_type == "reverse":
        return name[::-1]
    else:
        return f"Unknown format type: {format_type}. Available: uppercase, lowercase, title, reverse"

async def main():
    """Main function to run the MCP server."""
    # Run the server
    await mcp.run()

if __name__ == "__main__":
    asyncio.run(main())
