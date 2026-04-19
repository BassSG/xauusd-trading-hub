"""
Data Fetcher Module for XAUUSD Trading Hub
Fetches gold price data from FMP API
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional
import urllib.request
import urllib.error

from config import (
    FMP_API_KEY, FMP_BASE_URL, SPOT_SYMBOL,
    DATA_JSON, FALLBACK_RESPONSE, FALLBACK_DATA
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches gold price and market data from FMP API"""
    
    def __init__(self, api_key: str = FMP_API_KEY):
        self.api_key = api_key
        self.base_url = FMP_BASE_URL
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request to FMP API with error handling"""
        try:
            url = f"{self.base_url}/{endpoint}"
            if params:
                param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                url += f"?{param_str}&apikey={self.api_key}"
            else:
                url += f"?apikey={self.api_key}"
            
            logger.info(f"Fetching: {url[:80]}...")
            
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/json')
            
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
    
    def get_gold_quote(self) -> Optional[Dict]:
        """Get current gold price quote"""
        # Try spot XAUUSD first, then futures
        symbols = [SPOT_SYMBOL, "GC00Y", "XAUUSDUSD"]
        
        for symbol in symbols:
            data = self._make_request(f"quote/{symbol}")
            if data and len(data) > 0:
                quote = data[0]
                return {
                    "current_price": quote.get("price", 0),
                    "day_high": quote.get("dayHigh", 0),
                    "day_low": quote.get("dayLow", 0),
                    "volume": quote.get("volume", 0),
                    "avg_volume": quote.get("avgVolume", 0),
                    "52wk_high": quote.get("yearHigh", 0),
                    "52wk_low": quote.get("yearLow", 0),
                    "change": quote.get("change", 0),
                    "change_pct": quote.get("changesPercentage", 0),
                    "symbol": symbol
                }
        
        logger.warning("Could not fetch gold quote")
        return None
    
    def get_gold_historical(self, symbol: str = "XAUUSD") -> Optional[list]:
        """Get historical closing prices for gold"""
        data = self._make_request(f"historical-price-full/{symbol}", {
            "timeseries": "60"  # Last 60 days
        })
        
        if data and "historical" in data:
            closes = [h["close"] for h in data["historical"]]
            return closes[-60:]  # Last 60 closing prices
        
        return None
    
    def calculate_ma(self, closes: list, period: int) -> float:
        """Calculate Moving Average"""
        if len(closes) < period:
            return sum(closes) / len(closes) if closes else 0
        return sum(closes[-period:]) / period
    
    def calculate_volatility(self, closes: list) -> tuple:
        """Calculate price volatility"""
        if len(closes) < 2:
            return 0, 0
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(closes)):
            if closes[i-1] != 0:
                ret = (closes[i] - closes[i-1]) / closes[i-1] * 100
                returns.append(ret)
        
        if not returns:
            return 0, 0
        
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        
        # Annualized volatility
        volatility = std_dev * (252 ** 0.5)
        volatility_pct = volatility
        
        return volatility, volatility_pct
    
    def determine_trend(self, closes: list) -> str:
        """Determine market trend based on price action"""
        if len(closes) < 50:
            return "Unknown"
        
        ma50 = self.calculate_ma(closes, 50)
        ma200 = self.calculate_ma(closes, 200) if len(closes) >= 200 else self.calculate_ma(closes, len(closes)//2)
        current = closes[-1]
        
        if current > ma50 > ma200:
            return "Uptrend"
        elif current < ma50 < ma200:
            return "Downtrend"
        else:
            return "Sideways"
    
    def fetch_all_data(self) -> Dict:
        """Fetch all gold data and compile into data.json format"""
        result = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "FMP API",
            "error": None
        }
        
        # Get quote data
        quote = self.get_gold_quote()
        
        # Get historical data
        closes = self.get_gold_historical()
        
        if closes is None:
            # Try to use fallback data
            logger.warning("Using fallback data")
            result.update(FALLBACK_RESPONSE)
            result["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result["source"] = "FALLBACK"
            result["error"] = "API unavailable"
            return result
        
        # Calculate indicators
        ma50 = self.calculate_ma(closes, 50)
        ma200 = self.calculate_ma(closes, 200) if len(closes) >= 200 else ma50
        volatility, volatility_pct = self.calculate_volatility(closes)
        trend = self.determine_trend(closes)
        
        # Get high/low ranges
        high_5d = max(closes[-5:]) if len(closes) >= 5 else max(closes)
        low_5d = min(closes[-5:]) if len(closes) >= 5 else min(closes)
        high_20d = max(closes[-20:]) if len(closes) >= 20 else max(closes)
        low_20d = min(closes[-20:]) if len(closes) >= 20 else min(closes)
        
        # Compile result
        result.update({
            "current_price": quote.get("current_price", closes[-1]) if quote else closes[-1],
            "day_high": quote.get("day_high", high_5d) if quote else high_5d,
            "day_low": quote.get("day_low", low_5d) if quote else low_5d,
            "volume": quote.get("volume", 0) if quote else 0,
            "avg_volume": quote.get("avg_volume", 0) if quote else 0,
            "52wk_high": quote.get("52wk_high", max(closes)) if quote else max(closes),
            "52wk_low": quote.get("52wk_low", min(closes)) if quote else min(closes),
            "ma50": ma50,
            "ma200": ma200,
            "volatility": volatility,
            "volatility_pct": volatility_pct,
            "trend": trend,
            "high_5d": high_5d,
            "low_5d": low_5d,
            "high_20d": high_20d,
            "low_20d": low_20d,
            "closes": closes[-60:] if len(closes) > 60 else closes,
            "suffix": "Gold Futures"
        })
        
        return result
    
    def save_data(self, data: Dict, filepath: str = DATA_JSON) -> bool:
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {str(e)}")
            return False


def main():
    """Main function for standalone execution"""
    logger.info("Starting Gold Data Fetcher...")
    
    fetcher = DataFetcher()
    data = fetcher.fetch_all_data()
    
    if data:
        fetcher.save_data(data)
        logger.info(f"Current Gold Price: ${data.get('current_price', 'N/A')}")
        logger.info(f"Trend: {data.get('trend', 'N/A')}")
        logger.info(f"RSI based on data: {data.get('rsi', 'N/A')}")
    else:
        logger.error("Failed to fetch data")


if __name__ == "__main__":
    main()
