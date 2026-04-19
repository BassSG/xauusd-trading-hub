#!/usr/bin/env python3
"""
Data Update Script for XAUUSD Trading Hub
Fetches all data, updates JSON files, and commits to GitHub

Usage:
    python update_data.py              # Update all data
    python update_data.py --data      # Update price data only
    python update_data.py --indicators # Update indicators only
    python update_data.py --sentiment  # Update sentiment only
    python update_data.py --calendar  # Update calendar only
    python update_data.py --briefing  # Generate daily briefing only
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime

# Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from config import GITHUB_TOKEN, GITHUB_USER, GITHUB_REPO, GITHUB_EMAIL, GITHUB_NAME
from data_fetcher import DataFetcher
from indicators import IndicatorCalculator
from sentiment import SentimentAnalyzer
from economic_calendar import EconomicCalendarFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_git_command(command: list, cwd: str = BASE_DIR) -> tuple:
    """Run git command and return output"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Git command timed out"
    except Exception as e:
        return False, "", str(e)


def commit_and_push(message: str) -> bool:
    """Commit changes and push to GitHub"""
    logger.info("Committing changes to GitHub...")
    
    # Set git identity
    run_git_command([
        "git", "config", "--local", "user.email", GITHUB_EMAIL
    ])
    run_git_command([
        "git", "config", "--local", "user.name", GITHUB_NAME
    ])
    
    # Stage all changes
    success, stdout, stderr = run_git_command(["git", "add", "-A"])
    if not success:
        logger.error(f"Git add failed: {stderr}")
        return False
    
    # Check if there are changes
    success, stdout, _ = run_git_command(["git", "status", "--porcelain"])
    if not stdout.strip():
        logger.info("No changes to commit")
        return True
    
    # Commit
    success, stdout, stderr = run_git_command([
        "git", "commit", "-m", message
    ])
    if not success:
        logger.error(f"Git commit failed: {stderr}")
        return False
    
    # Push
    success, stdout, stderr = run_git_command([
        "git", "push", "origin", "main"
    ])
    if not success:
        logger.error(f"Git push failed: {stderr}")
        return False
    
    logger.info("✅ Successfully pushed to GitHub")
    return True


def update_price_data() -> dict:
    """Update gold price data"""
    logger.info("📊 Fetching gold price data...")
    fetcher = DataFetcher()
    data = fetcher.fetch_all_data()
    if data:
        fetcher.save_data(data)
        logger.info(f"✅ Price updated: ${data.get('current_price', 'N/A')}")
    return data or {}


def update_indicators() -> dict:
    """Update technical indicators"""
    logger.info("📈 Calculating technical indicators...")
    calc = IndicatorCalculator()
    calc.load_price_data()
    indicators = calc.calculate_all_indicators()
    if indicators:
        calc.save_indicators(indicators)
        logger.info(f"✅ Indicators updated: RSI={indicators.get('rsi')}")
    return indicators or {}


def update_sentiment() -> dict:
    """Update sentiment analysis"""
    logger.info("🎯 Analyzing market sentiment...")
    analyzer = SentimentAnalyzer()
    sentiment = analyzer.fetch_and_analyze()
    if sentiment:
        analyzer.save_sentiment(sentiment)
        logger.info(f"✅ Sentiment updated: {sentiment['sentiment']['overall']}")
    return sentiment or {}


def update_calendar() -> dict:
    """Update economic calendar"""
    logger.info("📅 Fetching economic calendar...")
    fetcher = EconomicCalendarFetcher()
    events = fetcher.get_economic_calendar(days=7)
    if events:
        fetcher.save_calendar(events)
        logger.info(f"✅ Calendar updated: {len(events)} events")
    return {"events": events, "count": len(events)}


def generate_briefing() -> str:
    """Generate daily briefing"""
    logger.info("📝 Generating daily briefing...")
    
    # Load all data
    DATA_JSON_PATH = os.path.join(BASE_DIR, "gold-analysis", "data.json")
    INDICATORS_JSON_PATH = os.path.join(BASE_DIR, "gold-analysis", "indicators.json")
    SENTIMENT_JSON_PATH = os.path.join(BASE_DIR, "gold-analysis", "sentiment.json")
    
    try:
        with open(DATA_JSON_PATH, 'r') as f:
            price_data = json.load(f)
        with open(INDICATORS_JSON_PATH, 'r') as f:
            indicators = json.load(f)
        with open(SENTIMENT_JSON_PATH, 'r') as f:
            sentiment = json.load(f)
        
        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")
        
        briefing = f"""# 📊 XAUUSD Daily Briefing - {date_str}

*Generated: {today.strftime('%H:%M:%S')} UTC*

## 💰 Gold Price: ${price_data.get('current_price', 'N/A')}

**Trend**: {price_data.get('trend', 'Unknown')} | **Volatility**: {price_data.get('volatility_pct', 0):.2f}%

## 📈 Technical Indicators

| Indicator | Value |
|-----------|-------|
| RSI (14) | {indicators.get('rsi', 'N/A')} |
| MACD | {indicators.get('macd', 0):.4f} |
| Signal | {indicators.get('signal', 0):.4f} |

**Support**: {indicators.get('support_zone', ['N/A'])[:3]}
**Resistance**: {indicators.get('resistance_zone', ['N/A'])[:3]}

## 🎯 Sentiment: {sentiment['sentiment']['overall']} ({sentiment['sentiment']['score']}/100)

{sentiment.get('summary', 'No summary available')}

*Data sourced from FMP API, Brave Search, and Travily*
"""
        
        briefing_path = os.path.join(BASE_DIR, "daily-briefings", f"{date_str}-daily-briefing.md")
        with open(briefing_path, 'w', encoding='utf-8') as f:
            f.write(briefing)
        
        logger.info(f"✅ Briefing saved: {briefing_path}")
        return briefing_path
        
    except Exception as e:
        logger.error(f"❌ Failed to generate briefing: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="XAUUSD Data Update Script")
    parser.add_argument("--data", action="store_true", help="Update price data only")
    parser.add_argument("--indicators", action="store_true", help="Update indicators only")
    parser.add_argument("--sentiment", action="store_true", help="Update sentiment only")
    parser.add_argument("--calendar", action="store_true", help="Update calendar only")
    parser.add_argument("--briefing", action="store_true", help="Generate briefing only")
    parser.add_argument("--no-push", action="store_true", help="Skip GitHub push")
    
    args = parser.parse_args()
    
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # If no specific option, run all
    run_all = not any([args.data, args.indicators, args.sentiment, args.calendar, args.briefing])
    
    results = []
    
    if run_all or args.data:
        update_price_data()
        results.append("price_data")
    
    if run_all or args.indicators:
        update_indicators()
        results.append("indicators")
    
    if run_all or args.sentiment:
        update_sentiment()
        results.append("sentiment")
    
    if run_all or args.calendar:
        update_calendar()
        results.append("calendar")
    
    if run_all or args.briefing:
        generate_briefing()
        results.append("briefing")
    
    # Commit to GitHub
    if not args.no_push:
        if results:
            commit_message = f"🔄 Auto-update: {', '.join(results)} ({today})"
            commit_and_push(commit_message)
    
    logger.info(f"✅ Update complete: {', '.join(results) if results else 'Nothing to update'}")


if __name__ == "__main__":
    main()
