# Bedtime Story Generator - Cron Instructions

When you receive a message about generating the daily bedtime story:

1. **Run the generator script:**
   ```bash
   python3 /data/data/com.termux/files/home/.openclaw/workspace/bedtime-story/generate_story_deepseek.py
   ```

2. **What the script does:**
   - Generates a bilingual (English/Chinese) bedtime story using DeepSeek API
   - Updates `stories.json` with today's date
   - Commits and pushes to GitHub automatically
   - Skips if story for today already exists

3. **Expected output:**
   - Script prints "Story saved. Total: X" on success
   - If push fails, it prints "Committed locally (push failed)"

4. **Location:**
   - Script: `generate_story_deepseek.py`
   - Stories file: `stories.json`
   - Repository: https://github.com/pipiilgatto/bedtime-stories

**Important:** Just run the script. No need for additional actions unless there's an error.