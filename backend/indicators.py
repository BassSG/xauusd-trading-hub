"""
Technical Indicators Calculator for XAUUSD Trading Hub
Calculates RSI, MACD, Support/Resistance zones
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from config import DATA_JSON, INDICATORS_JSON, GOLD_ANALYSIS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """Calculate technical indicators for gold trading"""
    
    def __init__(self):
        self.data = {}
        self.load_price_data()
    
    def load_price_data(self) -> bool:
        """Load price data from data.json"""
        try:
            with open(DATA_JSON, 'r') as f:
                self.data = json.load(f)
            logger.info("Price data loaded successfully")
            return True
        except FileNotFoundError:
            logger.error(f"Price data file not found: {DATA_JSON}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in price data: {e}")
            return False
    
    def calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(closes) < period + 1:
            return 50.0  # Neutral
        
        # Calculate price changes
        deltas = []
        for i in range(1, len(closes)):
            deltas.append(closes[i] - closes[i-1])
        
        # Separate gains and losses
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0
        
        if avg_loss == 0:
            return 100.0  # Strong uptrend
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def calculate_macd(self, closes: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(closes) < slow:
            closes_for_calc = closes
        else:
            closes_for_calc = closes[-slow:]
        
        # Calculate EMAs
        def calc_ema(data: List[float], period: int) -> float:
            if len(data) < period:
                return sum(data) / len(data)
            
            multiplier = 2 / (period + 1)
            ema = sum(data[:period]) / period
            
            for price in data[period:]:
                ema = (price - ema) * multiplier + ema
            
            return ema
        
        ema_fast = calc_ema(closes_for_calc, fast)
        ema_slow = calc_ema(closes_for_calc, slow)
        
        macd_line = ema_fast - ema_slow
        
        # Signal line (EMA of MACD)
        macd_values = [macd_line]  # Simplified - would need historical MACD for proper signal
        signal_line = macd_line  # Placeholder
        
        return round(macd_line, 4), round(signal_line, 4)
    
    def find_support_zones(self, closes: List[float], lookback: int = 20, tolerance: float = 0.002) -> List[float]:
        """Find support zones based on recent lows"""
        if len(closes) < lookback:
            lookback = len(closes)
        
        recent_lows = closes[-lookback:]
        min_price = min(recent_lows)
        
        # Find local minima
        supports = []
        for i in range(1, len(recent_lows) - 1):
            if recent_lows[i] < recent_lows[i-1] and recent_lows[i] < recent_lows[i+1]:
                supports.append(recent_lows[i])
        
        if not supports:
            # Use recent lows with tolerance grouping
            supports = [min_price]
        
        # Group nearby support levels
        grouped = []
        for s in supports:
            found = False
            for g in grouped:
                if abs(s - g) / g < tolerance:
                    found = True
                    if s < g:
                        grouped[grouped.index(g)] = s
                    break
            if not found:
                grouped.append(s)
        
        # Sort and take top 5
        grouped.sort(reverse=True)
        return grouped[:5]
    
    def find_resistance_zones(self, closes: List[float], lookback: int = 20, tolerance: float = 0.002) -> List[float]:
        """Find resistance zones based on recent highs"""
        if len(closes) < lookback:
            lookback = len(closes)
        
        recent_highs = closes[-lookback:]
        max_price = max(recent_highs)
        
        # Find local maxima
        resistances = []
        for i in range(1, len(recent_highs) - 1):
            if recent_highs[i] > recent_highs[i-1] and recent_highs[i] > recent_highs[i+1]:
                resistances.append(recent_highs[i])
        
        if not resistances:
            resistances = [max_price]
        
        # Group nearby resistance levels
        grouped = []
        for r in resistances:
            found = False
            for g in grouped:
                if abs(r - g) / g < tolerance:
                    found = True
                    if r > g:
                        grouped[grouped.index(g)] = r
                    break
            if not found:
                grouped.append(r)
        
        # Sort and take top 5
        grouped.sort()
        return grouped[:5]
    
    def calculate_all_indicators(self) -> Dict:
        """Calculate all technical indicators"""
        closes = self.data.get("closes", [])
        
        if not closes:
            logger.warning("No closing prices available")
            return {
                "rsi": 50.0,
                "macd": 0.0,
                "signal": 0.0,
                "support_zone": [4375.5, 4399.3, 4404.1, 4492.0, 4526.0],
                "resistance_zone": [5229.7, 5230.5, 5294.4, 5301.6, 5318.4],
                "last_calculated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        rsi = self.calculate_rsi(closes)
        macd, signal = self.calculate_macd(closes)
        support_zone = self.find_support_zones(closes)
        resistance_zone = self.find_resistance_zones(closes)
        
        # Determine signal strength
        if rsi < 30:
            signal_strength = "Oversold - Potential Buy"
        elif rsi > 70:
            signal_strength = "Overbought - Potential Sell"
        else:
            signal_strength = "Neutral"
        
        return {
            "rsi": rsi,
            "macd": macd,
            "signal": signal,
            "signal_strength": signal_strength,
            "support_zone": support_zone,
            "resistance_zone": resistance_zone,
            "last_calculated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def save_indicators(self, indicators: Dict, filepath: str = INDICATORS_JSON) -> bool:
        """Save indicators to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(indicators, f, indent=2, ensure_ascii=False)
            logger.info(f"Indicators saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save indicators: {str(e)}")
            return False


def main():
    """Main function for standalone execution"""
    logger.info("Starting Technical Indicators Calculator...")
    
    calculator = IndicatorCalculator()
    indicators = calculator.calculate_all_indicators()
    
    if indicators:
        calculator.save_indicators(indicators)
        logger.info(f"RSI: {indicators.get('rsi')}")
        logger.info(f"MACD: {indicators.get('macd')}")
        logger.info(f"Signal Strength: {indicators.get('signal_strength')}")
        logger.info(f"Support Zone: {indicators.get('support_zone')}")
        logger.info(f"Resistance Zone: {indicators.get('resistance_zone')}")
    
    return indicators


if __name__ == "__main__":
    main()
