#!/bin/bash

# Docker Setup Script for Bluetooth Manager
echo "🐳 Setting up Bluetooth Manager with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   https://docs.docker.com/desktop/install/mac-install/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

# Install blueutil for native macOS Bluetooth control
echo "📦 Installing blueutil for native macOS Bluetooth control..."
if ! command -v brew &> /dev/null; then
    echo "⚠️  Homebrew not found. Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

brew install blueutil

# Verify blueutil installation
if command -v blueutil &> /dev/null; then
    echo "✅ blueutil installed successfully"
    echo "Current Bluetooth status: $(blueutil -p)"
else
    echo "❌ Failed to install blueutil"
    exit 1
fi

echo "🎉 Docker setup complete!"
echo ""
echo "To run the host server (on Mac 1):"
echo "   ./scripts/start-host.sh"
echo ""
echo "To run the client (on Mac 2):"
echo "   ./scripts/start-client.sh <HOST_IP>"
echo ""
echo "Or use native Python (non-Docker):"
echo "   ./scripts/setup-native.sh"
