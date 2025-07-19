#!/bin/bash

# Default credentials
DEFAULT_USERNAME="admin"
DEFAULT_PASSWORD="bluetooth123"

# Parse command line arguments
USERNAME=${1:-$DEFAULT_USERNAME}
PASSWORD=${2:-$DEFAULT_PASSWORD}

# Set authentication credentials
export BT_USERNAME="$USERNAME"
export BT_PASSWORD="$PASSWORD"

echo "Starting Bluetooth Switch with authentication..."
echo "Username: $USERNAME"
echo "Password: $PASSWORD"
echo ""
echo "Usage: $0 [username] [password]"
echo "Example: $0 myuser mypassword"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go to the parent directory (project root) then into host
cd "$SCRIPT_DIR/../host"
python3 app.py
