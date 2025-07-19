#!/bin/bash

# Start Host Server with Docker
echo "🚀 Starting Bluetooth Manager Host Server..."

cd "$(dirname "$0")/.."

# Get local IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")

echo "🎯 Starting host server at: $LOCAL_IP:5000"
echo "📱 Access from your phone: http://$LOCAL_IP:5000"

# Build and start the host container
docker-compose -f docker/docker-compose.yml up --build

echo ""
echo "🛑 Host server stopped"
