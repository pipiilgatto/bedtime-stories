#!/usr/bin/env python3
"""
Generate a bilingual bedtime story using DeepSeek API and commit to GitHub.
"""

import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

# Configuration
DEEPSEEK_API_KEY = "sk-1acfdf3f4db34e23b395dcb45ec31ed1"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-reasoner"
STORIES_FILE = Path(__file__).parent / "stories.json"
REPO_DIR = Path(__file__).parent.parent
MAX_STORIES = 30

def get_today_date():
    return datetime.now().strftime("%Y-%m-%d")

def load_stories():
    if not STORIES_FILE.exists():
        return []
    try:
        with open(STORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_stories(stories):
    with open(STORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)

def generate_story():
    prompt = """You are a warm, creative storyteller. Write a short, original bedtime story that is heartwarming and suitable for all ages.
The story should be exactly 3–5 paragraphs long, with a gentle moral or uplifting message.

Please provide the story in **both English and Chinese**.
Format your response exactly as follows:

ENGLISH:
[story in English]

CHINESE:
[story in Chinese]

Keep the language simple, poetic, and comforting. Avoid any scary or sad elements."""

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
        "temperature": 0.8
    }

    try:
        response = requests.post(
            DEEPSEEK_URL,
            json=payload,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        raw_text = result['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error calling DeepSeek API: {e}", file=sys.stderr)
        return None

    # Parse English and Chinese
    english, chinese = "", ""
    lines = raw_text.split('\n')
    in_english, in_chinese = False, False
    
    for line in lines:
        line = line.strip()
        if line.upper().startswith("ENGLISH:"):
            in_english, in_chinese = True, False
            continue
        elif line.upper().startswith("CHINESE:"):
            in_english, in_chinese = False, True
            continue
        if in_english and line:
            english += line + "\n"
        if in_chinese and line:
            chinese += line + "\n"

    # Fallback parsing
    if not english or not chinese:
        parts = raw_text.split('\n\n')
        if len(parts) >= 2:
            english, chinese = parts[0].strip(), parts[1].strip()
        else:
            english = chinese = raw_text

    return {"en": english.strip(), "zh": chinese.strip()}

def git_commit_push(message="Update stories"):
    """Commit and push to GitHub."""
    os.chdir(REPO_DIR)
    os.system("git add bedtime-story/stories.json 2>/dev/null")
    os.system(f"git commit -m '{message}' 2>/dev/null")
    result = os.system("git push origin master 2>&1")
    return result == 0

def main():
    today = get_today_date()
    stories = load_stories()

    # Skip if already generated today
    if any(s.get("date") == today for s in stories):
        print(f"Story for {today} already exists. Skipping.", file=sys.stderr)
        sys.exit(0)

    print(f"Generating story for {today}...", file=sys.stderr)
    story_content = generate_story()
    if not story_content:
        print("Failed to generate story.", file=sys.stderr)
        sys.exit(1)

    new_story = {
        "date": today,
        "en": story_content["en"],
        "zh": story_content["zh"]
    }

    stories.insert(0, new_story)
    stories = stories[:MAX_STORIES]
    save_stories(stories)

    print(f"Story saved. Total: {len(stories)}", file=sys.stderr)
    
    # Commit and push
    msg = f"Add story for {today}"
    if git_commit_push(msg):
        print("Committed and pushed to GitHub!", file=sys.stderr)
    else:
        print("Committed locally (push failed - check token).", file=sys.stderr)

if __name__ == "__main__":
    main()
