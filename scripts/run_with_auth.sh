#!/bin/bash

# Default credentials
DEFAULT_USERNAME="admin"
DEFAULT_PASSWORD="bluetooth123"
DEFAULT_API_KEY="bluetooth-switch-secure-api-key-change-me"

# Parse command line arguments
USERNAME=${1:-$DEFAULT_USERNAME}
PASSWORD=${2:-$DEFAULT_PASSWORD}
API_KEY=${3:-$DEFAULT_API_KEY}

# Set authentication credentials
export BT_USERNAME="$USERNAME"
export BT_PASSWORD="$PASSWORD"
export BT_API_KEY="$API_KEY"

echo "Starting Bluetooth Switch with authentication..."
echo "Username: $USERNAME"
echo "Password: $PASSWORD"
echo "API Key: ${API_KEY:0:20}..."
echo ""
echo "Usage: $0 [username] [password] [api_key]"
echo "Example: $0 myuser mypassword my-secure-api-key"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go to the parent directory (project root) then into host
cd "$SCRIPT_DIR/../host"
python3 app.py
