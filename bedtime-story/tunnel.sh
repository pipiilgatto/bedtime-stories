#!/data/data/com.termux/files/usr/bin/bash
# SSH tunnel for bedtime story server

set -e

PORT=3000
LOG_FILE="tunnel.log"
PID_FILE="tunnel.pid"

# Kill existing tunnel
if [ -f "$PID_FILE" ]; then
    kill $(cat "$PID_FILE") 2>/dev/null && echo "Killed existing tunnel"
    sleep 1
fi

echo "Starting SSH tunnel to localhost.run (port $PORT)..."

# Start tunnel in background, capture output
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -N -R 80:localhost:$PORT nokey@localhost.run > "$LOG_FILE" 2>&1 &
TUNNEL_PID=$!

# Save PID
echo $TUNNEL_PID > "$PID_FILE"

echo "Tunnel started with PID $TUNNEL_PID"
echo "Logs: $LOG_FILE"

# Wait a moment for connection, then extract URL
sleep 3
if [ -f "$LOG_FILE" ]; then
    echo "Checking for tunnel URL..."
    URL=$(grep -o "https://[a-z0-9-]*\.lhr\.life" "$LOG_FILE" | head -1)
    if [ -n "$URL" ]; then
        echo "Tunnel URL: $URL"
        echo "$URL" > tunnel.url
    else
        echo "URL not found yet. Check $LOG_FILE for details."
        tail -5 "$LOG_FILE"
    fi
fi