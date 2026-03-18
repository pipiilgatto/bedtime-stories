#!/data/data/com.termux/files/usr/bin/bash
# Start the bedtime story HTTP server

# Keep Termux awake (prevent Android from suspending)
termux-wake-lock 2>/dev/null

cd "$(dirname "$0")"
PORT=3000

# Check if server already running
if curl -s -o /dev/null http://127.0.0.1:${PORT}/status 2>/dev/null; then
    echo "Server already running on port ${PORT}."
    exit 0
fi

# Start Python server in background
nohup python3 serve.py > server.log 2>&1 &
SERVER_PID=$!

# Save PID to file
echo $SERVER_PID > server.pid

echo "Bedtime story server started (PID: $SERVER_PID)"
echo "Logs: server.log"
echo "To stop: kill $SERVER_PID"

# Get local IP
ip=$(ip addr show wlan0 2>/dev/null | grep -oP 'inet \K[\d.]+' | head -1)
if [ -z "$ip" ]; then
    ip=$(ip addr show 2>/dev/null | grep -oP 'inet \K[\d.]+' | grep -v '127.0.0.1' | head -1)
fi
if [ -n "$ip" ]; then
    echo "Access via: http://${ip}:${PORT}"
else
    echo "Access via: http://127.0.0.1:${PORT}"
fi