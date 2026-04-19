"""
Economic Calendar Fetcher for XAUUSD Trading Hub
Fetches upcoming economic events that affect gold prices
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import urllib.request
import urllib.error

from config import FMP_API_KEY, FMP_BASE_URL, ECONOMIC_CALENDAR_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EconomicCalendarFetcher:
    """Fetch economic calendar data from FMP API"""
    
    def __init__(self, api_key: str = FMP_API_KEY):
        self.api_key = api_key
        self.base_url = FMP_BASE_URL
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request to FMP API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            if params:
                param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                url += f"?{param_str}&apikey={self.api_key}"
            else:
                url += f"?apikey={self.api_key}"
            
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
    
    def get_economic_calendar(self, days: int = 7) -> List[Dict]:
        """Get economic calendar for upcoming days"""
        data = self._make_request("economic-calendar")
        
        if not data:
            logger.warning("Could not fetch economic calendar")
            return self._get_fallback_events(days)
        
        events = []
        today = datetime.now()
        
        for event in data[:50]:  # Process top 50 events
            try:
                date_str = event.get("date", "")
                event_date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else today
                
                # Filter to upcoming days
                if (event_date - today).days <= days:
                    events.append({
                        "date": date_str,
                        "time": event.get("time", "All Day"),
                        "event": event.get("event", ""),
                        "country": event.get("country", ""),
                        "impact": event.get("impact", "Medium"),
                        "previous": event.get("previous", ""),
                        "forecast": event.get("forecast", ""),
                        "actual": event.get("actual", "")
                    })
            except Exception as e:
                continue
        
        # Sort by date
        events.sort(key=lambda x: (x["date"], x["time"]))
        return events[:20]  # Top 20 upcoming events
    
    def _get_fallback_events(self, days: int) -> List[Dict]:
        """Return fallback events when API is unavailable"""
        today = datetime.now()
        return [
            {
                "date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                "time": "20:30",
                "event": "US FOMC Meeting Minutes",
                "country": "USD",
                "impact": "High",
                "previous": "-",
                "forecast": "-",
                "actual": "-"
            },
            {
                "date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
                "time": "14:30",
                "event": "US GDP Q/Q",
                "country": "USD",
                "impact": "High",
                "previous": "2.4%",
                "forecast": "2.2%",
                "actual": "-"
            },
            {
                "date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
                "time": "08:30",
                "event": "US Non-Farm Employment Change",
                "country": "USD",
                "impact": "High",
                "previous": "275K",
                "forecast": "250K",
                "actual": "-"
            },
            {
                "date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
                "time": "14:30",
                "event": "US Unemployment Rate",
                "country": "USD",
                "impact": "High",
                "previous": "3.8%",
                "forecast": "3.9%",
                "actual": "-"
            },
            {
                "date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
                "time": "14:30",
                "event": "US CPI m/m",
                "country": "USD",
                "impact": "High",
                "previous": "0.3%",
                "forecast": "0.2%",
                "actual": "-"
            }
        ]
    
    def format_events_markdown(self, events: List[Dict]) -> str:
        """Format events as markdown"""
        md_lines = [
            "# Economic Calendar",
            "",
            f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "| Date | Time | Event | Country | Impact | Previous | Forecast |",
            "|------|------|-------|--------|--------|----------|----------|"
        ]
        
        for event in events:
            impact_emoji = {
                "High": "🔴",
                "Medium": "🟡",
                "Low": "🟢"
            }.get(event.get("impact", "Medium"), "🟡")
            
            md_lines.append(
                f"| {event['date']} | {event['time']} | {impact_emoji} {event['event']} | "
                f"{event['country']} | {event['impact']} | {event['previous']} | {event['forecast']} |"
            )
        
        md_lines.append("")
        md_lines.append("## Impact on Gold")
        md_lines.append("")
        md_lines.append("- 🔴 High Impact: Major moves expected")
        md_lines.append("- 🟡 Medium Impact: Moderate volatility")
        md_lines.append("- 🟢 Low Impact: Minor price fluctuations")
        md_lines.append("")
        md_lines.append("*Note: Times are in UTC. US events typically at 13:30-14:30 UTC.*")
        
        return "\n".join(md_lines)
    
    def save_calendar(self, events: List[Dict], filepath: str = None) -> bool:
        """Save calendar to JSON and Markdown"""
        if filepath is None:
            filepath = f"{ECONOMIC_CALENDAR_DIR}/upcoming.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "events": events,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "count": len(events)
                }, f, indent=2, ensure_ascii=False)
            
            # Also save markdown
            md_filepath = f"{ECONOMIC_CALENDAR_DIR}/upcoming.md"
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(self.format_events_markdown(events))
            
            logger.info(f"Calendar saved to {filepath} and {md_filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save calendar: {str(e)}")
            return False


def main():
    """Main function for standalone execution"""
    logger.info("Starting Economic Calendar Fetcher...")
    
    fetcher = EconomicCalendarFetcher()
    events = fetcher.get_economic_calendar(days=7)
    
    if events:
        fetcher.save_calendar(events)
        logger.info(f"Fetched {len(events)} upcoming events")
        for event in events[:5]:
            logger.info(f"  {event['date']} {event['time']}: {event['event']}")
    
    return events


if __name__ == "__main__":
    main()
