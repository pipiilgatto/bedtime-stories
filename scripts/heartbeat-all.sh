#!/bin/bash
# Run all heartbeat checks and send Telegram notification

set -e

WORKSPACE="/data/data/com.termux/files/home/.openclaw/workspace"
SCRIPTS_DIR="$WORKSPACE/scripts"
LOG_FILE="$WORKSPACE/tmp/heartbeat-last.log"
STATE_FILE="$WORKSPACE/memory/heartbeat-state.json"

# Create tmp directory
mkdir -p "$WORKSPACE/tmp"

# Run all checks and capture output
{
    echo "=== Heartbeat Check $(date) ==="
    echo ""
    echo "--- News Headlines ---"
    bash "$SCRIPTS_DIR/heartbeat-news.sh"
    echo ""
    echo "--- Stock Prices ---"
    python3 "$SCRIPTS_DIR/heartbeat-stocks.py"
    echo ""
    echo "--- Service Status ---"
    bash "$SCRIPTS_DIR/heartbeat-service.sh"
} > "$LOG_FILE" 2>&1

# Check for critical issues in service status
CRITICAL_ISSUES=()
if ! ss -ltn 2>/dev/null | grep -q ':8443'; then
    CRITICAL_ISSUES+=("SSH port 8443 not listening")
fi

DATA_PCT=$(df /data 2>/dev/null | tail -1 | awk '{print $5}' | sed 's/%//')
if [ -n "$DATA_PCT" ] && [ "$DATA_PCT" -gt 90 ]; then
    CRITICAL_ISSUES+=("Data partition >90% full")
fi

# Check stock prices for unusual movement (>2%)
STOCK_ALERTS=()
STOCK_OUTPUT=$(python3 "$SCRIPTS_DIR/heartbeat-stocks.py" 2>/dev/null)
while IFS= read -r line; do
    if [[ $line =~ ([A-Z]+):\ \\$([0-9.]+)\ \(([+-][0-9.]+),\ ([+-][0-9.]+)%\) ]]; then
        symbol="${BASH_REMATCH[1]}"
        change_percent="${BASH_REMATCH[4]}"
        # Remove + sign for comparison
        change_abs=${change_percent#+}
        change_abs=${change_abs#-}
        if (( $(echo "$change_abs > 2.0" | bc -l 2>/dev/null || echo "$change_abs > 2" ) )); then
            STOCK_ALERTS+=("$symbol ${change_percent}%")
        fi
    fi
done <<< "$STOCK_OUTPUT"

# Update state file
TIMESTAMP=$(date +%s)
if [ -f "$STATE_FILE" ]; then
    jq --arg ts "$TIMESTAMP" '.lastChecks.news = ($ts|tonumber) | .lastChecks.stocks = ($ts|tonumber) | .lastChecks.service = ($ts|tonumber)' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
else
    echo "{\"lastChecks\": {\"news\": $TIMESTAMP, \"stocks\": $TIMESTAMP, \"service\": $TIMESTAMP}}" > "$STATE_FILE"
fi

# Prepare notification message
TIMESTAMP_HR=$(date '+%H:%M UTC')
if [ ${#CRITICAL_ISSUES[@]} -eq 0 ]; then
    BASE_MESSAGE="❤️ Heartbeat check completed at $TIMESTAMP_HR."
else
    ISSUES_STR=$(IFS=', '; echo "${CRITICAL_ISSUES[*]}")
    BASE_MESSAGE="⚠️ Heartbeat check at $TIMESTAMP_HR: ${ISSUES_STR}"
fi

# Add stock alerts if any
if [ ${#STOCK_ALERTS[@]} -gt 0 ]; then
    STOCK_STR=$(IFS=', '; echo "${STOCK_ALERTS[*]}")
    MESSAGE="$BASE_MESSAGE Stocks: $STOCK_STR"
else
    MESSAGE="$BASE_MESSAGE"
fi

# Send notification via Telegram Bot API
TELEGRAM_TOKEN="8715264713:AAHBdUdDQd2SoUlO2OcsL5IxZrXf6fWi90c"
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": \"8630376767\", \"text\": \"$MESSAGE\"}" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Telegram notification sent: $MESSAGE"
else
    echo "Failed to send Telegram notification"
fi

echo "Heartbeat checks completed. Log saved to $LOG_FILE"
echo "Notification sent: $MESSAGE"