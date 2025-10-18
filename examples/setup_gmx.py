#!/usr/bin/env python3
"""
GMX MCP Server Setup Script
Helps set up the GMX trading environment and configuration.
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        # Install from requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_gmx_sdk():
    """Set up the GMX Python SDK"""
    print("🔧 Setting up GMX Python SDK...")
    
    gmx_sdk_path = Path("gmx_python_sdk-main")
    
    if not gmx_sdk_path.exists():
        print("❌ GMX SDK directory not found. Please ensure gmx_python_sdk-main is in the current directory.")
        return False
    
    # Create config file if it doesn't exist
    config_path = gmx_sdk_path / "config.yaml"
    
    if not config_path.exists():
        default_config = {
            'rpcs': {
                'arbitrum': 'https://arbitrum.meowrpc.com',
                'avalanche': 'https://api.avax.network/ext/bc/C/rpc'
            },
            'chain_ids': {
                'arbitrum': 42161,
                'avalanche': 43114
            },
            'private_key': 'your_private_key_here',
            'user_wallet_address': 'your_wallet_address_here'
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"✅ Created default config file at {config_path}")
    else:
        print(f"✅ Config file already exists at {config_path}")
    
    return True

def create_mcp_config():
    """Create MCP configuration for Claude Desktop"""
    print("🤖 Creating MCP configuration for Claude Desktop...")
    
    # Determine the path to the current directory
    current_dir = os.path.abspath(os.getcwd())
    server_path = os.path.join(current_dir, "gmx_server.py")
    
    mcp_config = {
        "mcpServers": {
            "gmx-trading": {
                "command": "python",
                "args": [server_path],
                "env": {
                    "PYTHONPATH": current_dir
                }
            }
        }
    }
    
    # Create MCP config directory if it doesn't exist
    mcp_dir = Path.home() / ".config" / "claude-desktop"
    mcp_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = mcp_dir / "claude_desktop_config.json"
    
    # Read existing config or create new one
    import json
    existing_config = {}
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Existing config file is invalid, creating new one...")
    
    # Merge configurations
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"]["gmx-trading"] = mcp_config["mcpServers"]["gmx-trading"]
    
    # Write updated config
    with open(config_file, 'w') as f:
        json.dump(existing_config, f, indent=2)
    
    print(f"✅ MCP configuration created at {config_file}")
    print("📋 Configuration added:")
    print(json.dumps(mcp_config, indent=2))
    
    return True

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("🎉 GMX MCP Server Setup Complete!")
    print("="*60)
    
    print("\n📋 NEXT STEPS:")
    print("1. 🔄 Restart Claude Desktop to load the new MCP server")
    print("2. 🔐 Configure your wallet using: setup_wallet(private_key, wallet_address)")
    print("3. 📊 Test the connection with: help_gmx_trading()")
    
    print("\n💡 EXAMPLE COMMANDS TO TRY:")
    print("• help_gmx_trading() - Get list of all available commands")
    print("• get_market_data() - View available GMX markets")
    print("• get_oracle_prices() - Get current token prices")
    print("• estimate_swap_output('USDC', 'ETH', 100) - Estimate swap output")
    
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("• Keep your private key secure and never share it")
    print("• Always test with small amounts first")
    print("• Use debug_mode=True for testing (default)")
    print("• Set debug_mode=False only when ready to execute real trades")
    
    print("\n🔧 CONFIGURATION FILES:")
    print(f"• GMX Config: gmx_python_sdk-main/config.yaml")
    print(f"• MCP Config: ~/.config/claude-desktop/claude_desktop_config.json")
    
    print("\n🌐 SUPPORTED NETWORKS:")
    print("• Arbitrum (recommended)")
    print("• Avalanche (experimental)")

def main():
    """Main setup function"""
    print("🚀 GMX MCP Server Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Setup GMX SDK
    if not setup_gmx_sdk():
        print("❌ Setup failed during GMX SDK configuration")
        sys.exit(1)
    
    # Create MCP config
    if not create_mcp_config():
        print("❌ Setup failed during MCP configuration")
        sys.exit(1)
    
    # Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    main()
