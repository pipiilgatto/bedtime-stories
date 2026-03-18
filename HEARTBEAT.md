# HEARTBEAT.md - Periodic Tasks

Run the consolidated heartbeat check script every 2 hours:

```bash
/data/data/com.termux/files/home/.openclaw/workspace/scripts/heartbeat-all.sh
```

## What the script does:
1. Fetches top 5 news headlines from BBC RSS
2. Checks VOO and QQQ stock prices
3. Verifies service status (OpenClaw, SSH, disk, cron jobs)
4. Sends Telegram notification with status summary
5. Logs detailed output to `tmp/heartbeat-last.log`

## Telegram Notifications:
- ✅ No issues: "❤️ Heartbeat check completed at [time]. All systems OK."
- ⚠️ Issues: "⚠️ Heartbeat check at [time]: [issue1, issue2]"

## Response:
- If script runs successfully, reply HEARTBEAT_OK.
- If there are critical issues that need attention, describe them instead of HEARTBEAT_OK.
