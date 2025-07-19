#!/bin/bash

# Start Client (Native Python)
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <HOST_IP> [CLIENT_NAME] [API_KEY]"
    echo "Example: $0 192.168.1.100 MacBook-Pro my-secure-api-key"
    exit 1
fi

HOST_IP="$1"
CLIENT_NAME="${2:-$(hostname)}"
API_KEY="${3:-bluetooth-switch-secure-api-key-change-me}"

# Export API key for client to use
export BT_API_KEY="$API_KEY"

echo "🔌 Starting Bluetooth Manager Client (Native Python)..."
echo "🎯 Connecting to host: $HOST_IP"
echo "📱 Client name: $CLIENT_NAME"
echo "🔐 API Key: ${API_KEY:0:20}..."

cd "$(dirname "$0")/../client"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python3 app.py --host "$HOST_IP" --name "$CLIENT_NAME"
