#!/data/data/com.termux/files/usr/bin/bash
# Bore tunnel setup using precompiled binary

set -e

PORT=3000
BORE_DIR="/data/data/com.termux/files/home/.openclaw/workspace/bedtime-story/.bore"
BORE_BIN="$BORE_DIR/bore"
LOG_FILE="bore.log"
PID_FILE="bore.pid"

# Create directory
mkdir -p "$BORE_DIR"
cd "$BORE_DIR"

# Download bore binary if not exists
if [ ! -f "$BORE_BIN" ]; then
    echo "Downloading bore binary..."
    curl -L -o bore.tar.gz "https://github.com/ekzhang/bore/releases/download/v0.6.0/bore-v0.6.0-aarch64-unknown-linux-musl.tar.gz"
    tar -xzf bore.tar.gz
    mv bore-v0.6.0-aarch64-unknown-linux-musl/bore bore
    chmod +x bore
    rm -rf bore.tar.gz bore-v0.6.0-aarch64-unknown-linux-musl
    echo "Bore binary downloaded."
fi

# Kill existing tunnel
if [ -f "../$PID_FILE" ]; then
    kill $(cat "../$PID_FILE") 2>/dev/null && echo "Killed existing tunnel"
    sleep 1
fi

echo "Starting bore tunnel on port $PORT..."

# Start tunnel in background
"$BORE_BIN" local "$PORT" --to bore.pub > "../$LOG_FILE" 2>&1 &
BORE_PID=$!

# Save PID
echo $BORE_PID > "../$PID_FILE"

echo "Bore tunnel started with PID $BORE_PID"
echo "Logs: $LOG_FILE"

# Wait for URL to appear
sleep 3
if [ -f "../$LOG_FILE" ]; then
    echo "Checking for tunnel URL..."
    URL=$(grep -o "bore\.pub:[0-9]*" "../$LOG_FILE" | head -1)
    if [ -n "$URL" ]; then
        PUBLIC_URL="https://${URL/bore.pub:/}.bore.pub"
        echo "Tunnel URL: $PUBLIC_URL"
        echo "$PUBLIC_URL" > ../bore.url
    else
        echo "URL not found yet. Check $LOG_FILE for details."
        tail -10 "../$LOG_FILE"
    fi
fi