#!/usr/bin/env python3
"""
Daily spending report: summarize API token usage and costs.
"""
import json
import os
import sys
import datetime
import subprocess
from pathlib import Path

# Pricing per million tokens
PRICING = {
    "custom-api-deepseek-com": {
        "input": 0.14,
        "output": 0.28,
        "cacheRead": 0.014,
        "cacheWrite": 0.028
    },
    "minimax-cn": {
        "input": 0.30,
        "output": 1.20,
        "cacheRead": 0.03,
        "cacheWrite": 0.12
    },
    "ollama-remote": {
        "input": 0.0,
        "output": 0.0,
        "cacheRead": 0.0,
        "cacheWrite": 0.0
    }
}

def get_sessions_data():
    """Load session data from sessions.json."""
    sessions_path = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / "sessions.json"
    if not sessions_path.exists():
        return {}
    
    with open(sessions_path, 'r') as f:
        return json.load(f)

def calculate_spending(sessions):
    """Calculate token usage and spending from session data."""
    totals = {}
    
    for key, session in sessions.items():
        # Skip if no token data
        if session.get("totalTokensFresh") is False:
            continue
        
        model_provider = session.get("modelProvider")
        if not model_provider:
            # Some sessions have model directly without provider
            model = session.get("model", "")
            if "deepseek" in model.lower():
                model_provider = "custom-api-deepseek-com"
            elif "minimax" in model.lower():
                model_provider = "minimax-cn"
            elif "qwen" in model.lower() or "ollama" in model.lower():
                model_provider = "ollama-remote"
            else:
                continue
        
        # Initialize provider totals
        if model_provider not in totals:
            totals[model_provider] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cost": 0.0
            }
        
        # Add tokens (some sessions have inputTokens/outputTokens, others only totalTokens)
        input_tokens = session.get("inputTokens", 0)
        output_tokens = session.get("outputTokens", 0)
        total_tokens = session.get("totalTokens", 0)
        
        # If we have input/output, use those; otherwise estimate from total
        if input_tokens > 0 or output_tokens > 0:
            totals[model_provider]["input_tokens"] += input_tokens
            totals[model_provider]["output_tokens"] += output_tokens
        elif total_tokens:
            # Estimate 90% input, 10% output (typical ratio)
            totals[model_provider]["input_tokens"] += int(total_tokens * 0.9)
            totals[model_provider]["output_tokens"] += int(total_tokens * 0.1)
        
        totals[model_provider]["total_tokens"] += total_tokens
    
    # Calculate costs
    for provider, data in totals.items():
        pricing = PRICING.get(provider, PRICING["ollama-remote"])  # default to free
        input_cost = (data["input_tokens"] / 1_000_000) * pricing["input"]
        output_cost = (data["output_tokens"] / 1_000_000) * pricing["output"]
        data["cost"] = input_cost + output_cost
    
    return totals

def format_report(totals):
    """Format spending report as readable text."""
    lines = []
    lines.append("💰 **Daily Spending Report**")
    lines.append("")
    
    total_cost = 0
    total_input = 0
    total_output = 0
    
    # Sort providers by cost (highest first)
    sorted_providers = sorted(totals.items(), key=lambda x: x[1]["cost"], reverse=True)
    
    for provider, data in sorted_providers:
        if data["cost"] == 0 and data["total_tokens"] == 0:
            continue
            
        provider_name = provider
        if provider == "custom-api-deepseek-com":
            provider_name = "DeepSeek"
        elif provider == "minimax-cn":
            provider_name = "MiniMax"
        elif provider == "ollama-remote":
            provider_name = "Ollama (Qwen)"
        
        lines.append(f"**{provider_name}:**")
        lines.append(f"  Input:  {data['input_tokens']:,} tokens")
        lines.append(f"  Output: {data['output_tokens']:,} tokens")
        lines.append(f"  Total:  {data['total_tokens']:,} tokens")
        lines.append(f"  Cost:   ${data['cost']:.4f}")
        lines.append("")
        
        total_cost += data["cost"]
        total_input += data["input_tokens"]
        total_output += data["output_tokens"]
    
    lines.append("---")
    lines.append(f"**Grand Total:**")
    lines.append(f"  Input:  {total_input:,} tokens")
    lines.append(f"  Output: {total_output:,} tokens")
    lines.append(f"  Cost:   ${total_cost:.4f}")
    lines.append("")
    
    # Add pricing reference
    lines.append("**Pricing Reference:**")
    lines.append("  • DeepSeek: $0.14/M input, $0.28/M output")
    lines.append("  • MiniMax:  $0.30/M input, $1.20/M output")
    lines.append("  • Ollama:   Free (local)")
    
    return "\n".join(lines)

def send_telegram_notification(message):
    """Send a notification via Telegram using Bot API."""
    try:
        import urllib.request
        import urllib.error
        
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
    """Main function."""
    sessions = get_sessions_data()
    if not sessions:
        error_msg = "Daily spending report: No session data found."
        print(error_msg, file=sys.stderr)
        send_telegram_notification(error_msg)
        sys.exit(1)
    
    totals = calculate_spending(sessions)
    report = format_report(totals)
    print(report)
    
    # Create short summary for Telegram
    total_cost = sum(data["cost"] for data in totals.values())
    total_tokens = sum(data["total_tokens"] for data in totals.values())
    
    # Find top provider
    top_provider = max(totals.items(), key=lambda x: x[1]["cost"]) if totals else None
    if top_provider:
        provider_name = top_provider[0]
        if provider_name == "custom-api-deepseek-com":
            provider_name = "DeepSeek"
        elif provider_name == "minimax-cn":
            provider_name = "MiniMax"
        elif provider_name == "ollama-remote":
            provider_name = "Ollama"
        top_cost = top_provider[1]["cost"]
        top_pct = (top_cost / total_cost * 100) if total_cost > 0 else 0
        summary = f"💰 Spending report: ${total_cost:.4f} total, {total_tokens:,} tokens. Top: {provider_name} (${top_cost:.4f}, {top_pct:.1f}%)"
    else:
        summary = f"💰 Spending report: ${total_cost:.4f} total, {total_tokens:,} tokens."
    
    send_telegram_notification(summary)

if __name__ == "__main__":
    main()