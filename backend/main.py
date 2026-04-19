"""
Main Orchestrator for XAUUSD Trading Hub Backend
Coordinates all data fetching, processing, and GitHub updates
"""

import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    GITHUB_USER, GITHUB_REPO, GITHUB_TOKEN, GITHUB_EMAIL, GITHUB_NAME,
    BASE_DIR, GOLD_ANALYSIS_DIR, DAILY_BRIEFINGS_DIR,
    DATA_JSON, INDICATORS_JSON, SENTIMENT_JSON
)
from data_fetcher import DataFetcher
from indicators import IndicatorCalculator
from sentiment import SentimentAnalyzer
from economic_calendar import EconomicCalendarFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackendOrchestrator:
    """Main orchestrator for backend operations"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.indicator_calculator = IndicatorCalculator()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.economic_fetcher = EconomicCalendarFetcher()
        
        self.last_run = None
        self.status = {
            "data": False,
            "indicators": False,
            "sentiment": False,
            "calendar": False
        }
    
    def update_price_data(self) -> Dict:
        """Fetch and update gold price data"""
        logger.info("=" * 50)
        logger.info("Step 1: Fetching Gold Price Data...")
        
        try:
            data = self.data_fetcher.fetch_all_data()
            if data:
                success = self.data_fetcher.save_data(data, DATA_JSON)
                self.status["data"] = success
                logger.info(f"✅ Gold price data updated: ${data.get('current_price', 'N/A')}")
                return data
            else:
                logger.error("❌ Failed to fetch price data")
                return {}
        except Exception as e:
            logger.error(f"❌ Error updating price data: {str(e)}")
            return {}
    
    def update_indicators(self) -> Dict:
        """Calculate and update technical indicators"""
        logger.info("=" * 50)
        logger.info("Step 2: Calculating Technical Indicators...")
        
        try:
            # Reload price data first
            self.indicator_calculator.load_price_data()
            indicators = self.indicator_calculator.calculate_all_indicators()
            
            if indicators:
                success = self.indicator_calculator.save_indicators(indicators, INDICATORS_JSON)
                self.status["indicators"] = success
                logger.info(f"✅ Indicators updated - RSI: {indicators.get('rsi')}")
                return indicators
            else:
                logger.error("❌ Failed to calculate indicators")
                return {}
        except Exception as e:
            logger.error(f"❌ Error updating indicators: {str(e)}")
            return {}
    
    def update_sentiment(self) -> Dict:
        """Fetch news and update sentiment analysis"""
        logger.info("=" * 50)
        logger.info("Step 3: Analyzing Market Sentiment...")
        
        try:
            sentiment_data = self.sentiment_analyzer.fetch_and_analyze()
            
            if sentiment_data:
                success = self.sentiment_analyzer.save_sentiment(sentiment_data, SENTIMENT_JSON)
                self.status["sentiment"] = success
                logger.info(f"✅ Sentiment updated: {sentiment_data['sentiment']['overall']}")
                return sentiment_data
            else:
                logger.error("❌ Failed to fetch sentiment")
                return {}
        except Exception as e:
            logger.error(f"❌ Error updating sentiment: {str(e)}")
            return {}
    
    def update_calendar(self) -> Dict:
        """Fetch and update economic calendar"""
        logger.info("=" * 50)
        logger.info("Step 4: Fetching Economic Calendar...")
        
        try:
            events = self.economic_fetcher.get_economic_calendar(days=7)
            
            if events:
                success = self.economic_fetcher.save_calendar(events)
                self.status["calendar"] = success
                logger.info(f"✅ Calendar updated: {len(events)} events")
                return {"events": events, "count": len(events)}
            else:
                logger.error("❌ Failed to fetch calendar")
                return {}
        except Exception as e:
            logger.error(f"❌ Error updating calendar: {str(e)}")
            return {}
    
    def generate_daily_briefing(self) -> str:
        """Generate daily briefing markdown report"""
        logger.info("=" * 50)
        logger.info("Step 5: Generating Daily Briefing...")
        
        try:
            # Load all data
            with open(DATA_JSON, 'r') as f:
                price_data = json.load(f)
            
            with open(INDICATORS_JSON, 'r') as f:
                indicators = json.load(f)
            
            with open(SENTIMENT_JSON, 'r') as f:
                sentiment_data = json.load(f)
            
            today = datetime.now()
            date_str = today.strftime("%Y-%m-%d")
            day_name = today.strftime("%A")
            
            # Generate briefing
            briefing = f"""# 📊 XAUUSD Daily Briefing - {date_str} ({day_name})

*Generated: {today.strftime('%H:%M:%S')} UTC | Source: XAUUSD Trading Hub Backend*

---

## 💰 Gold Price Overview

| Metric | Value |
|--------|-------|
| **Current Price** | ${price_data.get('current_price', 'N/A'):.2f} |
| **Day High** | ${price_data.get('day_high', 'N/A'):.2f} |
| **Day Low** | ${price_data.get('day_low', 'N/A'):.2f} |
| **52-Week High** | ${price_data.get('52wk_high', 'N/A'):.2f} |
| **52-Week Low** | ${price_data.get('52wk_low', 'N/A'):.2f} |
| **Trend** | {price_data.get('trend', 'Unknown')} |
| **Volatility** | {price_data.get('volatility_pct', 0):.2f}% |

### Moving Averages
- **MA50**: ${price_data.get('ma50', 0):.2f}
- **MA200**: ${price_data.get('ma200', 0):.2f}

---

## 📈 Technical Indicators

| Indicator | Value | Signal |
|-----------|-------|--------|
| **RSI (14)** | {indicators.get('rsi', 'N/A')} | {indicators.get('signal_strength', 'N/A')} |
| **MACD** | {indicators.get('macd', 0):.4f} | - |
| **Signal** | {indicators.get('signal', 0):.4f} | - |

### Support Zones
"""
            
            support_zones = indicators.get('support_zone', [])
            for i, zone in enumerate(support_zones, 1):
                briefing += f"- Zone {i}: **${zone:.2f}**\n"
            
            briefing += "\n### Resistance Zones\n"
            
            resistance_zones = indicators.get('resistance_zone', [])
            for i, zone in enumerate(resistance_zones, 1):
                briefing += f"- Zone {i}: **${zone:.2f}**\n"
            
            briefing += f"""
---

## 🎯 Market Sentiment

**Overall**: {sentiment_data['sentiment']['overall']} ({sentiment_data['sentiment']['score']}/100)

| Category | Count |
|----------|-------|
| Bullish | {sentiment_data['sentiment'].get('bullish_count', 0)} |
| Bearish | {sentiment_data['sentiment'].get('bearish_count', 0)} |
| Neutral | {sentiment_data['sentiment'].get('neutral_count', 0)} |

### Summary
{sentiment_data.get('summary', 'No summary available')}

---

## 📰 Latest News

"""
            
            news = sentiment_data.get('news', [])[:5]
            for i, item in enumerate(news, 1):
                briefing += f"""### {i}. {item.get('title', 'No title')}

{item.get('description', 'No description available')}

*Source: {item.get('source', 'Unknown')}* | [Read More]({item.get('url', '#')})

"""
            
            briefing += f"""---

## 🔔 Risk Management Tips

1. **Monitor RSI**: {'Overbought - Consider taking profits' if indicators.get('rsi', 50) > 70 else 'Oversold - Potential buying opportunity' if indicators.get('rsi', 50) < 30 else 'Neutral - No extreme signal'}
2. **Watch Support/Resistance**: Price is trading between ${price_data.get('low_20d', 0):.2f} - ${price_data.get('high_20d', 0):.2f}
3. **Trend Confirmation**: Current trend is **{price_data.get('trend', 'Unknown')}**
4. **Volatility Alert**: Current volatility at {price_data.get('volatility_pct', 0):.2f}%

---

*Data sourced from FMP API, Brave Search, and Travily*
*Last updated: {today.strftime('%Y-%m-%d %H:%M:%S')} UTC*

"""
            
            # Save briefing
            briefing_path = f"{DAILY_BRIEFINGS_DIR}/{date_str}-daily-briefing.md"
            with open(briefing_path, 'w', encoding='utf-8') as f:
                f.write(briefing)
            
            logger.info(f"✅ Daily briefing saved: {briefing_path}")
            return briefing_path
            
        except Exception as e:
            logger.error(f"❌ Error generating briefing: {str(e)}")
            return None
    
    def run_all(self) -> Dict:
        """Run all update operations"""
        logger.info("🚀" + "=" * 48)
        logger.info("XAUUSD Trading Hub - Backend Update Starting")
        logger.info("=" * 50)
        
        self.last_run = datetime.now()
        
        # Update all data sources
        results = {
            "price_data": self.update_price_data(),
            "indicators": self.update_indicators(),
            "sentiment": self.update_sentiment(),
            "calendar": self.update_calendar()
        }
        
        # Generate daily briefing
        briefing_path = self.generate_daily_briefing()
        
        # Summary
        logger.info("=" * 50)
        logger.info("📊 UPDATE SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Price Data: {'✅' if self.status['data'] else '❌'}")
        logger.info(f"Indicators: {'✅' if self.status['indicators'] else '❌'}")
        logger.info(f"Sentiment: {'✅' if self.status['sentiment'] else '❌'}")
        logger.info(f"Calendar: {'✅' if self.status['calendar'] else '❌'}")
        logger.info(f"Briefing: {'✅' if briefing_path else '❌'}")
        logger.info("=" * 50)
        
        return {
            "status": self.status,
            "results": results,
            "briefing_path": briefing_path,
            "last_run": self.last_run.isoformat()
        }


def main():
    """Main entry point"""
    logger.info("Starting XAUUSD Trading Hub Backend...")
    
    orchestrator = BackendOrchestrator()
    results = orchestrator.run_all()
    
    # Print summary
    print("\n" + "=" * 50)
    print("🎯 FINAL RESULTS")
    print("=" * 50)
    
    if results["results"]["price_data"]:
        print(f"💰 Gold Price: ${results['results']['price_data'].get('current_price', 'N/A')}")
    if results["results"]["indicators"]:
        print(f"📈 RSI: {results['results']['indicators'].get('rsi')}")
    if results["results"]["sentiment"]:
        print(f"🎯 Sentiment: {results['results']['sentiment']['sentiment']['overall']}")
    
    success_count = sum(results["status"].values())
    print(f"\n✅ {success_count}/4 data sources updated successfully")
    
    return results


if __name__ == "__main__":
    main()
