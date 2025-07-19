#!/bin/bash

# Start Client with Docker
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <HOST_IP>"
    echo "Example: $0 192.168.1.100"
    exit 1
fi

HOST_IP="$1"
CLIENT_NAME="${2:-$(hostname)}"

echo "🔌 Starting Bluetooth Manager Client..."
echo "🎯 Connecting to host: $HOST_IP"
echo "📱 Client name: $CLIENT_NAME"

cd "$(dirname "$0")/.."

# Export environment variables for docker-compose
export HOST_IP="$HOST_IP"
export CLIENT_NAME="$CLIENT_NAME"

# Build and start the client container
docker-compose -f docker/docker-compose.client.yml up --build

echo ""
echo "🛑 Client stopped"
