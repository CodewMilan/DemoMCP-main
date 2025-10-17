#!/bin/bash

# FastMCP Name Server Setup Script

echo "Setting up FastMCP Name Server..."
echo "================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python version: $python_version"

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies. Please check your Python/pip installation."
    exit 1
fi

echo ""
echo "Setup complete! 🎉"
echo ""
echo "To run the server:"
echo "  python3 server.py"
echo ""
echo "To test the server:"
echo "  python3 test_client.py"
echo ""
echo "For more information, see README.md"
