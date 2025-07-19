#!/bin/bash

# Start Host Server (Native Python)
echo "🐍 Starting Bluetooth Manager Host Server (Native Python)..."

cd "$(dirname "$0")/../host"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Get local IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")

echo "🎯 Starting host server at: $LOCAL_IP:5000"
echo "📱 Access from your phone: http://$LOCAL_IP:5000"

python3 app.py
