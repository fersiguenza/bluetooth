#!/bin/bash

# Kill processes script
echo "🔪 Killing processes on ports 5000 and 5001..."

# Function to kill processes on a port
kill_port() {
    local port=$1
    echo "Checking port $port..."
    
    # Get all PIDs using the port
    pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "Found processes on port $port: $pids"
        
        # Try normal kill first
        echo "$pids" | xargs kill 2>/dev/null
        sleep 2
        
        # Check if still running and force kill
        remaining_pids=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$remaining_pids" ]; then
            echo "Force killing remaining processes: $remaining_pids"
            echo "$remaining_pids" | xargs kill -9 2>/dev/null
            sleep 1
        fi
        
        # Final check
        final_check=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$final_check" ]; then
            echo "⚠️  Some processes may require sudo. Trying with sudo..."
            echo "$final_check" | xargs sudo kill -9 2>/dev/null
        fi
    else
        echo "✅ Port $port is free"
    fi
}

# Kill processes on both ports
kill_port 5000
kill_port 5001

echo ""
echo "✅ Port cleanup complete!"
echo ""

# Verify ports are free
echo "🔍 Verifying ports are free..."
port_5000_check=$(lsof -ti:5000 2>/dev/null)
port_5001_check=$(lsof -ti:5001 2>/dev/null)

if [ -z "$port_5000_check" ] && [ -z "$port_5001_check" ]; then
    echo "✅ Both ports 5000 and 5001 are now free!"
else
    echo "⚠️  Some processes may still be running:"
    [ -n "$port_5000_check" ] && echo "   Port 5000: $port_5000_check"
    [ -n "$port_5001_check" ] && echo "   Port 5001: $port_5001_check"
fi

echo ""
echo "💡 You can now start the server with:"
echo "   cd host && python3 app.py"
