"""
XAUUSD Trading Hub API Server
FastAPI-based REST API for dashboard consumption
"""

import json
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_JSON = BASE_DIR / "gold-analysis" / "data.json"
INDICATORS_JSON = BASE_DIR / "gold-analysis" / "indicators.json"
SENTIMENT_JSON = BASE_DIR / "gold-analysis" / "sentiment.json"
ECONOMIC_JSON = BASE_DIR / "economic-calendar" / "upcoming.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="XAUUSD Trading Hub API",
    description="Backend API for Gold Trading Dashboard",
    version="1.0.0"
)

# CORS for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response Models
class GoldPrice(BaseModel):
    current_price: float
    trend: str
    day_high: float
    day_low: float
    volume: int
    ma50: float
    ma200: float
    volatility_pct: float
    last_updated: str


class Indicators(BaseModel):
    rsi: float
    macd: float
    signal: float
    signal_strength: str
    support_zone: list
    resistance_zone: list
    last_calculated: str


class Sentiment(BaseModel):
    overall: str
    score: float
    bullish_count: int
    bearish_count: int
    neutral_count: int
    summary: str
    news_count: int


class EconomicEvent(BaseModel):
    date: str
    time: str
    event: str
    country: str
    impact: str
    previous: str
    forecast: str


class DashboardData(BaseModel):
    gold_price: GoldPrice
    indicators: Indicators
    sentiment: Sentiment
    economic_events: list
    api_timestamp: str


# Helper functions
def load_json(filepath: Path) -> dict:
    """Load JSON file with fallback"""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return {}


def get_fallback_data() -> dict:
    """Return fallback data when main data unavailable"""
    return {
        "error": "Using fallback data",
        "current_price": 4879.60,
        "trend": "Sideways",
        "rsi": 50.0
    }


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "XAUUSD Trading Hub API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/gold-price", response_model=GoldPrice)
async def get_gold_price():
    """Get current gold price data"""
    data = load_json(DATA_JSON)
    
    if not data:
        raise HTTPException(status_code=404, detail="Gold price data not found")
    
    return GoldPrice(
        current_price=data.get("current_price", 0),
        trend=data.get("trend", "Unknown"),
        day_high=data.get("day_high", 0),
        day_low=data.get("day_low", 0),
        volume=data.get("volume", 0),
        ma50=data.get("ma50", 0),
        ma200=data.get("ma200", 0),
        volatility_pct=data.get("volatility_pct", 0),
        last_updated=data.get("last_updated", "")
    )


@app.get("/api/indicators", response_model=Indicators)
async def get_indicators():
    """Get technical indicators"""
    data = load_json(INDICATORS_JSON)
    
    if not data:
        raise HTTPException(status_code=404, detail="Indicators data not found")
    
    return Indicators(
        rsi=data.get("rsi", 50),
        macd=data.get("macd", 0),
        signal=data.get("signal", 0),
        signal_strength=data.get("signal_strength", "Neutral"),
        support_zone=data.get("support_zone", []),
        resistance_zone=data.get("resistance_zone", []),
        last_calculated=data.get("last_calculated", "")
    )


@app.get("/api/sentiment", response_model=Sentiment)
async def get_sentiment():
    """Get market sentiment"""
    data = load_json(SENTIMENT_JSON)
    
    if not data:
        raise HTTPException(status_code=404, detail="Sentiment data not found")
    
    sentiment = data.get("sentiment", {})
    return Sentiment(
        overall=sentiment.get("overall", "Neutral"),
        score=sentiment.get("score", 50),
        bullish_count=sentiment.get("bullish_count", 0),
        bearish_count=sentiment.get("bearish_count", 0),
        neutral_count=sentiment.get("neutral_count", 0),
        summary=data.get("summary", ""),
        news_count=sentiment.get("news_count", 0)
    )


@app.get("/api/economic-calendar")
async def get_economic_calendar():
    """Get economic calendar events"""
    data = load_json(ECONOMIC_JSON)
    
    events = data.get("events", [])
    return {
        "events": events,
        "count": len(events),
        "last_updated": data.get("last_updated", "")
    }


@app.get("/api/dashboard", response_model=DashboardData)
async def get_dashboard():
    """Get all dashboard data in one request"""
    price_data = load_json(DATA_JSON)
    indicators_data = load_json(INDICATORS_JSON)
    sentiment_data = load_json(SENTIMENT_JSON)
    calendar_data = load_json(ECONOMIC_JSON)
    
    return DashboardData(
        gold_price=GoldPrice(
            current_price=price_data.get("current_price", 0),
            trend=price_data.get("trend", "Unknown"),
            day_high=price_data.get("day_high", 0),
            day_low=price_data.get("day_low", 0),
            volume=price_data.get("volume", 0),
            ma50=price_data.get("ma50", 0),
            ma200=price_data.get("ma200", 0),
            volatility_pct=price_data.get("volatility_pct", 0),
            last_updated=price_data.get("last_updated", "")
        ),
        indicators=Indicators(
            rsi=indicators_data.get("rsi", 50),
            macd=indicators_data.get("macd", 0),
            signal=indicators_data.get("signal", 0),
            signal_strength=indicators_data.get("signal_strength", "Neutral"),
            support_zone=indicators_data.get("support_zone", []),
            resistance_zone=indicators_data.get("resistance_zone", []),
            last_calculated=indicators_data.get("last_calculated", "")
        ),
        sentiment=Sentiment(
            overall=sentiment_data.get("sentiment", {}).get("overall", "Neutral"),
            score=sentiment_data.get("sentiment", {}).get("score", 50),
            bullish_count=sentiment_data.get("sentiment", {}).get("bullish_count", 0),
            bearish_count=sentiment_data.get("sentiment", {}).get("bearish_count", 0),
            neutral_count=sentiment_data.get("sentiment", {}).get("neutral_count", 0),
            summary=sentiment_data.get("summary", ""),
            news_count=sentiment_data.get("sentiment", {}).get("news_count", 0)
        ),
        economic_events=calendar_data.get("events", [])[:5],  # Top 5 events
        api_timestamp=datetime.utcnow().isoformat()
    )


@app.get("/api/history")
async def get_price_history():
    """Get historical closing prices"""
    data = load_json(DATA_JSON)
    closes = data.get("closes", [])
    
    return {
        "closes": closes,
        "count": len(closes),
        "last_updated": data.get("last_updated", "")
    }


# Run with: uvicorn api:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
