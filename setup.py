#!/usr/bin/env python3
"""
Simple setup script for GMX MCP Server
"""

import os
import shutil
import subprocess
import sys

def main():
    print("GMX MCP Server Setup")
    print("=" * 30)
    
    # Install dependencies
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return
    
    # Create .env.local if it doesn't exist
    if not os.path.exists('.env.local'):
        if os.path.exists('config/env.example'):
            shutil.copy('config/env.example', '.env.local')
            print("Created .env.local from template")
            print("Please edit .env.local with your wallet details")
        else:
            print("Please create .env.local with your wallet configuration")
    else:
        print(".env.local already exists")
    
    # Create config directory
    os.makedirs('config', exist_ok=True)
    print("Configuration directory ready")
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Edit .env.local with your wallet details")
    print("2. Run: python src/gmx_server.py")
    print("3. Add examples/claude_desktop_config.json to Claude Desktop")

if __name__ == "__main__":
    main()
