"""
XAUUSD Trading Hub Backend
Backend Integration Agent for automated data fetching and updates
"""

__version__ = "1.0.0"
__author__ = "Backend Agent"

from .config import *
from .data_fetcher import DataFetcher
from .indicators import IndicatorCalculator
from .sentiment import SentimentAnalyzer
from .economic_calendar import EconomicCalendarFetcher
from .main import BackendOrchestrator

__all__ = [
    "DataFetcher",
    "IndicatorCalculator", 
    "SentimentAnalyzer",
    "EconomicCalendarFetcher",
    "BackendOrchestrator"
]
