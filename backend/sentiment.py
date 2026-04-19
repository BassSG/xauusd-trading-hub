"""
Sentiment Analyzer for XAUUSD Trading Hub
Fetches news from Brave Search and analyzes market sentiment
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import urllib.request
import urllib.error
import urllib.parse

from config import (
    BRAVE_SEARCH_KEY, TRAVILY_KEY,
    SENTIMENT_JSON, SENTIMENT_JSON
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze market sentiment from news sources"""
    
    def __init__(self):
        self.brave_key = BRAVE_SEARCH_KEY
        self.travily_key = TRAVILY_KEY
        self.gold_keywords = [
            "gold price", "XAUUSD", "gold futures", "gold market",
            "gold trading", "gold rally", "gold drop", "gold outlook",
            "Fed gold", "dollar gold", "gold safe haven"
        ]
    
    def _make_brave_request(self, url: str, headers: Dict = None) -> Optional[Dict]:
        """Make request to Brave Search API"""
        try:
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/json")
            req.add_header("X-Subscription-Token", self.brave_key)
            
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
                
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP Error {e.code}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            logger.error(f"URL Error: {e.reason}")
            return None
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return None
    
    def search_gold_news(self, query: str = "gold price XAUUSD today", count: int = 10) -> List[Dict]:
        """Search for gold-related news using Brave Search"""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.search.brave.com/res/v1/news/search?q={encoded_query}&count={count}"
            
            result = self._make_brave_request(url)
            
            if result and "results" in result:
                news_items = []
                for item in result["results"][:count]:
                    news_items.append({
                        "title": item.get("title", ""),
                        "description": item.get("description", ""),
                        "url": item.get("url", ""),
                        "date": item.get("age", ""),
                        "source": item.get("meta_url", {}).get("netloc", "Unknown")
                    })
                return news_items
            
            return []
            
        except Exception as e:
            logger.error(f"Brave Search failed: {str(e)}")
            return []
    
    def search_travily(self, query: str = "gold market analysis") -> List[Dict]:
        """Search using Travily API for additional market data"""
        try:
            url = f"https://api.travily.com/search"
            data = json.dumps({
                "query": query,
                "limit": 5
            }).encode('utf-8')
            
            req = urllib.request.Request(url, data=data)
            req.add_header("Content-Type", "application/json")
            req.add_header("Authorization", f"Bearer {self.travily_key}")
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("results", [])
                
        except Exception as e:
            logger.error(f"Travily Search failed: {str(e)}")
            return []
    
    def analyze_sentiment(self, news: List[Dict]) -> Dict:
        """Analyze sentiment from news items"""
        if not news:
            return {
                "overall": "Neutral",
                "bullish_count": 0,
                "bearish_count": 0,
                "neutral_count": 0,
                "score": 50,
                "summary": "No news data available"
            }
        
        bullish_keywords = [
            "rally", "surge", "jump", "gain", "rise", "bullish",
            "high", "up", "growth", "optimism", "safe haven", "inflation"
        ]
        bearish_keywords = [
            "drop", "fall", "decline", "plunge", "bearish", "low",
            "down", "loss", "pessimism", "weak", "correction", "resistance"
        ]
        
        bullish = 0
        bearish = 0
        neutral = 0
        
        for item in news:
            text = f"{item.get('title', '')} {item.get('description', '')}".lower()
            
            b_count = sum(1 for kw in bullish_keywords if kw in text)
            be_count = sum(1 for kw in bearish_keywords if kw in text)
            
            if b_count > be_count:
                bullish += 1
            elif be_count > b_count:
                bearish += 1
            else:
                neutral += 1
        
        total = len(news)
        score = ((bullish - bearish + total) / (2 * total)) * 100
        
        if score > 60:
            overall = "Bullish"
        elif score < 40:
            overall = "Bearish"
        else:
            overall = "Neutral"
        
        return {
            "overall": overall,
            "bullish_count": bullish,
            "bearish_count": bearish,
            "neutral_count": neutral,
            "score": round(score, 1),
            "news_count": total
        }
    
    def generate_summary(self, sentiment: Dict, news: List[Dict]) -> str:
        """Generate a human-readable sentiment summary"""
        overall = sentiment.get("overall", "Neutral")
        score = sentiment.get("score", 50)
        
        summary_parts = []
        
        if overall == "Bullish":
            summary_parts.append(f"Market sentiment is BULLISH (Score: {score}/100)")
        elif overall == "Bearish":
            summary_parts.append(f"Market sentiment is BEARISH (Score: {score}/100)")
        else:
            summary_parts.append(f"Market sentiment is NEUTRAL (Score: {score}/100)")
        
        summary_parts.append(f"Based on {sentiment.get('news_count', 0)} news articles.")
        
        if sentiment.get("bullish_count", 0) > sentiment.get("bearish_count", 0):
            summary_parts.append("More positive catalysts than negative.")
        elif sentiment.get("bearish_count", 0) > sentiment.get("bullish_count", 0):
            summary_parts.append("More negative catalysts than positive.")
        
        return " ".join(summary_parts)
    
    def fetch_and_analyze(self) -> Dict:
        """Fetch news and analyze sentiment"""
        logger.info("Fetching gold news from Brave Search...")
        news = self.search_gold_news("gold price XAUUSD market today", count=10)
        
        logger.info("Fetching additional market data from Travily...")
        travily_results = self.search_travily("gold market analysis")
        
        sentiment = self.analyze_sentiment(news)
        summary = self.generate_summary(sentiment, news)
        
        # Combine news from both sources
        all_news = news.copy()
        for item in travily_results[:5]:
            all_news.append({
                "title": item.get("title", ""),
                "description": item.get("snippet", ""),
                "url": item.get("url", ""),
                "source": "Travily"
            })
        
        return {
            "sentiment": sentiment,
            "summary": summary,
            "news": all_news[:15],  # Keep top 15
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sources": {
                "brave": len(news),
                "travily": len(travily_results)
            }
        }
    
    def save_sentiment(self, data: Dict, filepath: str = SENTIMENT_JSON) -> bool:
        """Save sentiment data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Sentiment saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save sentiment: {str(e)}")
            return False


def main():
    """Main function for standalone execution"""
    logger.info("Starting Sentiment Analyzer...")
    
    analyzer = SentimentAnalyzer()
    result = analyzer.fetch_and_analyze()
    
    if result:
        analyzer.save_sentiment(result)
        logger.info(f"Overall Sentiment: {result['sentiment']['overall']}")
        logger.info(f"Score: {result['sentiment']['score']}/100")
        logger.info(f"Summary: {result['summary']}")
    
    return result


if __name__ == "__main__":
    main()
