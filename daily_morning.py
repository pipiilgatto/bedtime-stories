#!/usr/bin/env python3
"""
Daily morning report: weather, Chinese lunar calendar, health check, cat song.
"""
import json
import subprocess
import sys
import datetime
import random
import urllib.request
import urllib.error
from zhdate import ZhDate

def get_weather():
    """Return weather summary using get_weather.py."""
    try:
        result = subprocess.run(
            [sys.executable, '/data/data/com.termux/files/home/.openclaw/workspace/get_weather.py'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Weather error: {result.stderr[:100]}"
    except Exception as e:
        return f"Weather failed: {e}"

def get_lunar_date():
    """Calculate Chinese lunar date using zhdate library."""
    try:
        today = datetime.datetime.today()
        lunar = ZhDate.from_datetime(today)
        # Extract zodiac from chinese string, e.g., "二零二六年正月二十八 丙午年 (马年)"
        chinese_str = lunar.chinese()
        # Find zodiac in parentheses
        import re
        zodiac_match = re.search(r'\(([^)]+)年\)', chinese_str)
        zodiac_cn = zodiac_match.group(1) if zodiac_match else ""
        
        # Map Chinese zodiac to English
        zodiac_map = {
            "鼠": "Rat", "牛": "Ox", "虎": "Tiger", "兔": "Rabbit",
            "龙": "Dragon", "蛇": "Snake", "马": "Horse", "羊": "Goat",
            "猴": "Monkey", "鸡": "Rooster", "狗": "Dog", "猪": "Pig"
        }
        zodiac_en = zodiac_map.get(zodiac_cn, zodiac_cn)
        
        return f"Lunar {lunar.lunar_year}-{lunar.lunar_month}-{lunar.lunar_day} ({zodiac_en})"
    except Exception as e:
        return f"Lunar calendar failed: {e}"

def health_check():
    """System health check."""
    checks = []
    try:
        uptime = subprocess.run(['uptime', '-p'], capture_output=True, text=True).stdout.strip()
        checks.append(f"⏱ {uptime}")
    except:
        pass
    try:
        disk = subprocess.run(['df', '-h', '/data'], capture_output=True, text=True).stdout.strip().split('\n')[-1]
        checks.append(f"💾 {disk}")
    except:
        pass
    try:
        mem = subprocess.run(['free', '-m'], capture_output=True, text=True).stdout.strip().split('\n')[1]
        parts = mem.split()
        if len(parts) >= 3:
            total, used, free = parts[1], parts[2], parts[3]
            checks.append(f"🧠 RAM: {used}M used, {free}M free of {total}M")
    except:
        pass
    try:
        gw = subprocess.run(['openclaw', 'gateway', 'status'],
                           capture_output=True, text=True, timeout=5)
        if gw.returncode == 0:
            checks.append("🚀 Gateway: running")
        else:
            checks.append("🚀 Gateway: unknown")
    except:
        pass
    return '\n'.join(checks) if checks else "No health data."

def cat_song():
    """Generate a short cat song (≤50 words)."""
    songs = [
        "Meow meow, whiskers twitch, / Sunbeam nap, a happy switch. / Pounce on shadows, chase the string, / Purring loud, my heart takes wing. 🐱",
        "Furry paws on midnight stroll, / Hunting bugs is my main goal. / Yawn and stretch, then curl up tight, / Dreaming of the moonlit night. 🐾",
        "I am a cat, sleek and sly, / Watch the birds that flutter by. / Nap all day, then zoom at three, / Life is good, just wait and see. 😺",
        "Tail up high, a swishy flag, / Rub against your favorite bag. / Purr machine on full‑time duty, / Cuteness overload, that's my beauty. 🎶",
        "Little paws go pitter‑pat, / What a clever little cat. / Chase the red dot, climb the tree, / Then come back to sit with me. 🌟"
    ]
    return random.choice(songs)

def send_telegram_notification(message):
    """Send a notification via Telegram using Bot API."""
    try:
        import urllib.request
        import urllib.error
        import json
        
        token = "8715264713:AAHBdUdDQd2SoUlO2OcsL5IxZrXf6fWi90c"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": "8630376767",
            "text": message
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            if result.get("ok"):
                print(f"Telegram notification sent: {message[:50]}...", file=sys.stderr)
            else:
                print(f"Telegram API error: {result.get('description')}", file=sys.stderr)
    except Exception as e:
        print(f"Error sending Telegram notification: {e}", file=sys.stderr)

def main():
    lines = []
    lines.append("🌅 **Good morning!**")
    lines.append("")
    lines.append("🌤 **Weather:** " + get_weather())
    lines.append("")
    lines.append("🌙 **Lunar calendar:** " + get_lunar_date())
    lines.append("")
    lines.append("📊 **Health check:**")
    lines.append(health_check())
    lines.append("")
    lines.append("🐱 **Cat song of the day:**")
    lines.append(cat_song())
    full_report = '\n'.join(lines)
    print(full_report)
    
    # Send short notification
    # Extract weather summary (first line after "Weather: ")
    weather_line = get_weather()
    weather_summary = weather_line.split('.')[0] if '.' in weather_line else weather_line[:50]
    
    # Extract health check status
    health = health_check()
    health_status = "✅" if "No health data" in health or "OK" in health else "⚠️"
    
    notification = f"🌅 Morning report ready. Weather: {weather_summary} {health_status}"
    send_telegram_notification(notification)

if __name__ == '__main__':
    main()