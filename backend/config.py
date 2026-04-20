"""
Configuration for XAUUSD Trading Hub Backend
API Keys and Settings

NOTE: API keys should be set via environment variables:
  - FMP_API_KEY
  - BRAVE_SEARCH_KEY
  - TRAVILY_KEY
  - GITHUB_TOKEN
"""

import os

# API Keys (from environment variables)
FMP_API_KEY = os.environ.get("FMP_API_KEY", "YOUR_FMP_API_KEY")
BRAVE_SEARCH_KEY = os.environ.get("BRAVE_SEARCH_KEY", "YOUR_BRAVE_SEARCH_KEY")
TRAVILY_KEY = os.environ.get("TRAVILY_KEY", "YOUR_TRAVILY_KEY")

# GitHub Configuration
GITHUB_USER = "BassSG"
GITHUB_REPO = "xauusd-trading-hub"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_EMAIL = "agent@hermes.ai"
GITHUB_NAME = "Backend Agent"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_ANALYSIS_DIR = os.path.join(BASE_DIR, "gold-analysis")
DAILY_BRIEFINGS_DIR = os.path.join(BASE_DIR, "daily-briefings")
ECONOMIC_CALENDAR_DIR = os.path.join(BASE_DIR, "economic-calendar")

# Data Files
DATA_JSON = os.path.join(GOLD_ANALYSIS_DIR, "data.json")
INDICATORS_JSON = os.path.join(GOLD_ANALYSIS_DIR, "indicators.json")
SENTIMENT_JSON = os.path.join(GOLD_ANALYSIS_DIR, "sentiment.json")
FALLBACK_DATA = os.path.join(GOLD_ANALYSIS_DIR, "fallback.json")

# API Endpoints
FMP_BASE_URL = "https://financialmodelingprep.com/api"
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1"
TRAVILY_URL = "https://api.travily.com"

# TradingView Symbol for Gold
XAUUSD_SYMBOL = "GC00Y"  # Gold Futures
SPOT_SYMBOL = "XAUUSD"

# Default fallback data when APIs fail
FALLBACK_RESPONSE = {
    "current_price": 4879.60,
    "ma50": 4893.77,
    "ma200": 4187.54,
    "volatility": 153.63,
    "volatility_pct": 3.15,
    "trend": "Sideways",
    "rsi": 50.0,
    "macd": 0.0,
    "signal": 0.0,
    "support_zone": [4375.5, 4399.3, 4404.1, 4492.0, 4526.0],
    "resistance_zone": [5229.7, 5230.5, 5294.4, 5301.6, 5318.4]
}
