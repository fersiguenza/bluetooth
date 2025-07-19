#!/bin/bash

# Setup script for Bluetooth Manager
echo "🔵 Setting up Bluetooth Manager..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# Install blueutil if not already installed
echo "📦 Installing blueutil..."
brew install blueutil

# Verify blueutil installation
if command -v blueutil &> /dev/null; then
    echo "✅ blueutil installed successfully"
    echo "Current Bluetooth status: $(blueutil -p)"
else
    echo "❌ Failed to install blueutil"
    exit 1
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt

echo "🎉 Setup complete!"
echo ""
echo "To run the host server:"
echo "   python3 host.py"
echo ""
echo "To run the client on the other Mac:"
echo "   python3 client.py --host <HOST_IP>"
