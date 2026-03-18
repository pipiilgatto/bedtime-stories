#!/usr/bin/env python3
"""
Generate a bilingual bedtime story using Ollama and update stories.json
"""

import json
import os
import sys
from datetime import datetime, timedelta
import requests
import time

# Configuration
OLLAMA_URL = "http://192.168.1.11:11434"
MODEL = "qwen3.5:35b"
STORIES_FILE = os.path.join(os.path.dirname(__file__), "stories.json")
MAX_STORIES = 30  # Keep only the latest N stories

def get_today_date():
    """Return today's date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")

def load_stories():
    """Load existing stories from JSON file."""
    if not os.path.exists(STORIES_FILE):
        return []
    try:
        with open(STORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Warning: Could not load stories: {e}", file=sys.stderr)
        return []

def save_stories(stories):
    """Save stories list to JSON file."""
    with open(STORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)

def generate_story():
    """Generate a bilingual bedtime story using Ollama."""
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
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.8,
            "top_p": 0.95,
            "num_predict": 1500
        }
    }

    try:
        print(f"Calling Ollama at {OLLAMA_URL}/api/generate...", file=sys.stderr)
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        raw_text = result.get("response", "").strip()
        print(f"Raw response length: {len(raw_text)}", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama: {e}", file=sys.stderr)
        return None

    # Parse English and Chinese sections
    english = ""
    chinese = ""
    lines = raw_text.split('\n')
    in_english = False
    in_chinese = False
    for line in lines:
        line = line.strip()
        if line.lower().startswith("english:"):
            in_english = True
            in_chinese = False
            continue
        elif line.lower().startswith("chinese:"):
            in_english = False
            in_chinese = True
            continue
        if in_english and line:
            english += line + "\n"
        if in_chinese and line:
            chinese += line + "\n"

    # Fallback if parsing failed: split by two newlines and assume first half English, second half Chinese
    if not english or not chinese:
        parts = raw_text.strip().split('\n\n')
        if len(parts) >= 2:
            english = parts[0].strip()
            chinese = parts[1].strip()
        else:
            # Last resort: use raw text for both
            english = raw_text
            chinese = raw_text

    # Clean up extra whitespace
    english = english.strip()
    chinese = chinese.strip()

    return {"en": english, "zh": chinese}

def main():
    today = get_today_date()
    stories = load_stories()

    # Remove any existing story for today (so we can replace)
    stories = [s for s in stories if s.get("date") != today]

    print(f"Generating new story for {today}...", file=sys.stderr)
    story_content = generate_story()
    if not story_content:
        print("Failed to generate story.", file=sys.stderr)
        sys.exit(1)

    new_story = {
        "date": today,
        "en": story_content["en"],
        "zh": story_content["zh"]
    }

    # Insert at beginning (most recent first)
    stories.insert(0, new_story)

    # Trim to max stories
    if len(stories) > MAX_STORIES:
        stories = stories[:MAX_STORIES]

    save_stories(stories)
    print(f"Successfully added story for {today}. Total stories: {len(stories)}", file=sys.stderr)

if __name__ == "__main__":
    main()