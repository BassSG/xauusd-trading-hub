"""
News Agent for XAUUSD Trading Hub
Fetches news from FMP API, Brave Search, and Tavily
Combines, deduplicates, translates to Thai, and generates news.html
"""

import json
import logging
import sys
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import urllib.request
import urllib.error
import urllib.parse
import hashlib

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    FMP_API_KEY, FMP_BASE_URL,
    BRAVE_SEARCH_KEY, BRAVE_SEARCH_URL,
    TRAVILY_KEY, TRAVILY_URL,
    GITHUB_USER, GITHUB_REPO, GITHUB_TOKEN
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewsAgent:
    """Main news agent that fetches, processes, and generates news"""

    def __init__(self):
        self.fmp_key = FMP_API_KEY
        self.brave_key = BRAVE_SEARCH_KEY
        self.tavily_key = TRAVILY_KEY
        self.news_articles = []
        self.api_status = {
            "fmp": False,
            "brave": False,
            "tavily": False
        }

    def _make_request(self, url: str, headers: Dict = None, data: Dict = None) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            req = urllib.request.Request(url)
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)
            req.add_header('Accept', 'application/json')

            if data:
                req.data = urllib.parse.urlencode(data).encode('utf-8')

            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return None

    def fetch_fmp_news(self) -> List[Dict]:
        """Fetch news from FMP API"""
        logger.info("📡 Fetching news from FMP API...")
        news_list = []

        try:
            # FMP News API - correct endpoint for STARTER plan
            url = f"{FMP_BASE_URL}/v3/stock_news"
            params = {"tickers": "XAUUSD,gold", "limit": 15, "apikey": self.fmp_key}

            data = self._make_request(f"{url}?{'&'.join([f'{k}={v}' for k,v in params.items()])}")

            if data and isinstance(data, list):
                for item in data[:15]:
                    article = {
                        "id": hashlib.md5(item.get("url", "").encode()).hexdigest()[:12],
                        "title": item.get("title", ""),
                        "summary": item.get("text", item.get("content", "")),
                        "url": item.get("url", ""),
                        "image": item.get("image", ""),
                        "source": item.get("site", "FMP"),
                        "publishedAt": item.get("publishedDate", item.get("publishedAt", "")),
                        "category": self._categorize_article(item.get("title", "") + " " + item.get("text", "")),
                        "api": "FMP"
                    }
                    if article["title"]:
                        news_list.append(article)
                self.api_status["fmp"] = True
                logger.info(f"✅ FMP: Found {len(news_list)} articles")
            else:
                logger.warning("⚠️ FMP: No news data returned")
        except Exception as e:
            logger.error(f"❌ FMP Error: {str(e)}")

        return news_list

    def fetch_brave_news(self) -> List[Dict]:
        """Fetch news from Brave Search API"""
        logger.info("🔍 Fetching news from Brave Search...")
        news_list = []

        search_queries = [
            "gold price XAUUSD forecast",
            "Federal Reserve gold impact",
            "inflation gold trading",
            "central bank gold reserves"
        ]

        try:
            headers = {
                "X-Subscription-Token": self.brave_key,
                "Accept": "application/json"
            }

            for query in search_queries[:2]:  # Limit queries
                url = f"{BRAVE_SEARCH_URL}/news/search?q={urllib.parse.quote(query)}&count=10"
                data = self._make_request(url, headers=headers)

                if data and "results" in data:
                    for item in data["results"][:8]:
                        article = {
                            "id": hashlib.md5(item.get("url", "").encode()).hexdigest()[:12],
                            "title": item.get("title", ""),
                            "summary": item.get("description", item.get("snippet", "")),
                            "url": item.get("url", ""),
                            "source": item.get("meta_url", {}).get("domain", "Brave"),
                            "publishedAt": item.get("age", item.get("date", "")),
                            "category": self._categorize_article(item.get("title", "") + " " + item.get("description", "")),
                            "api": "Brave"
                        }
                        if article["title"]:
                            news_list.append(article)

            self.api_status["brave"] = True
            logger.info(f"✅ Brave: Found {len(news_list)} articles")
        except Exception as e:
            logger.error(f"❌ Brave Error: {str(e)}")

        return news_list

    def fetch_tavily_news(self) -> List[Dict]:
        """Fetch news from Tavily Search API"""
        logger.info("🌐 Fetching news from Tavily...")
        news_list = []

        search_queries = [
            "gold market outlook 2026",
            "central bank gold reserves buying"
        ]

        try:
            for query in search_queries:
                body = json.dumps({
                    "api_key": self.tavily_key,
                    "query": query,
                    "max_results": 8,
                    "search_depth": "advanced"
                }).encode('utf-8')

                req = urllib.request.Request(
                    f"{TRAVILY_URL}/search",
                    data=body,
                    headers={"Content-Type": "application/json", "Accept": "application/json"}
                )

                try:
                    with urllib.request.urlopen(req, timeout=30) as response:
                        data = json.loads(response.read().decode('utf-8'))
                except Exception as e:
                    logger.error(f"Request failed: {str(e)}")
                    continue

                if data and "results" in data:
                    for item in data["results"]:
                        article = {
                            "id": hashlib.md5(item.get("url", "").encode()).hexdigest()[:12],
                            "title": item.get("title", ""),
                            "summary": item.get("content", item.get("description", "")),
                            "url": item.get("url", ""),
                            "source": item.get("source", "Tavily"),
                            "publishedAt": item.get("published_date", item.get("publishedAt", "")),
                            "category": self._categorize_article(item.get("title", "") + " " + item.get("content", "")),
                            "api": "Tavily"
                        }
                        if article["title"]:
                            news_list.append(article)

            self.api_status["tavily"] = True
            logger.info(f"✅ Tavily: Found {len(news_list)} articles")
        except Exception as e:
            logger.error(f"❌ Tavily Error: {str(e)}")

        return news_list

    def _categorize_article(self, text: str) -> str:
        """Categorize article based on content"""
        text_lower = text.lower()

        if any(w in text_lower for w in ["war", "conflict", "military", "gulf", "middle east", "iran", "tension"]):
            return "war"
        elif any(w in text_lower for w in ["fed", "federal reserve", "interest rate", "powell", "monetary"]):
            return "fed"
        elif any(w in text_lower for w in ["inflation", "cpi", "ppi", "price index", "consumer price"]):
            return "inflation"
        elif any(w in text_lower for w in ["central bank", "reserve", "bank", "gold buying", " purchases"]):
            return "centralbank"
        else:
            return "price"

    def _translate_to_thai(self, text: str) -> str:
        """Translate text to Thai using MyMemory API (free)"""
        if not text:
            return text

        # Skip if already mostly Thai
        thai_chars = len(re.findall(r'[\u0E00-\u0E7F]', text))
        if thai_chars > len(text) * 0.3:
            return text

        try:
            encoded_text = urllib.parse.quote(text[:500].encode('utf-8'))
            url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair=en|th"
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("responseStatus") == 200:
                    translated = data.get("responseData", {}).get("translatedText", "")
                    if translated and translated != text:
                        return translated
        except Exception:
            pass

        # Fallback: simple word replacement
        translations = {
            "gold": "ทองคำ", "price": "ราคา", "forecast": "พยากรณ์",
            "outlook": "มุมมอง", "analysis": "วิเคราะห์", "surge": "พุ่ง",
            "rally": "กระโดด", "bullish": "ขาขึ้น", "bearish": "ขาลง",
            "market": "ตลาด", "trading": "การซื้อขาย", "dollar": "ดอลลาร์",
            "federal reserve": "ธนาคารกลางสหรัฐ", "fed": "เฟด",
            "inflation": "เงินเฟ้อ", "war": "สงคราม", "conflict": "ความขัดแย้ง",
            "tension": "ความตึงเครียด", "central bank": "ธนาคารกลาง",
            "resistance": "แนวต้าน", "support": "แนวรับ",
            "momentum": "โมเมนตัม", "volatile": "ผันผวน", "ounce": "ออนซ์",
            "spot": "ราคาปัจจุบัน", "high": "สูง", "low": "ต่ำ",
            "XAU/USD": "ทองคำ/ดอลลาร์", "up": "ขึ้น", "down": "ลง",
            "rise": "ขึ้น", "fall": "ลง", "drop": "ลง",
        }
        result = text
        for eng, thai in translations.items():
            result = re.sub(rf'\b{re.escape(eng)}\b', thai, result, flags=re.IGNORECASE)
        return result

    def _deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        seen_titles = set()
        unique_articles = []

        for article in articles:
            # Normalize title for comparison
            normalized = re.sub(r'[^\w\s]', '', article["title"].lower())
            normalized = re.sub(r'\s+', ' ', normalized).strip()

            if normalized not in seen_titles and len(normalized) > 10:
                seen_titles.add(normalized)
                unique_articles.append(article)

        return unique_articles

    def _format_time_ago(self, date_str: str) -> str:
        """Format timestamp to 'time ago' format in Thai"""
        if not date_str:
            return "ไม่ทราบเวลา"

        try:
            # Try parsing various date formats
            formats = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%B %d, %Y",
                "%b %d, %Y %H:%M:%S"
            ]

            dt = None
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str.replace("Z", "+0000")[:19], fmt)
                    break
                except:
                    pass

            if dt is None:
                # Check for relative time strings like "2 hours ago"
                match = re.search(r'(\d+)\s*(hour|hr|day|minute|min)', date_str.lower())
                if match:
                    num = int(match.group(1))
                    unit = match.group(2)
                    if 'hour' in unit or 'hr' in unit:
                        return f"{num} ชั่วโมงที่แล้ง"
                    elif 'minute' in unit or 'min' in unit:
                        return f"{num} นาทีที่แล้ง"
                    elif 'day' in unit:
                        return f"{num} วันที่แล้ง"

                return "เร็วๆ นี้"

            now = datetime.now()
            diff = now - dt

            if diff.days > 0:
                return f"{diff.days} วันที่แล้ง" if diff.days > 1 else "1 วันที่แล้ง"
            elif diff.seconds >= 3600:
                hours = diff.seconds // 3600
                return f"{hours} ชั่วโมงที่แล้ง" if hours > 1 else "1 ชั่วโมงที่แล้ง"
            elif diff.seconds >= 60:
                mins = diff.seconds // 60
                return f"{mins} นาทีที่แล้ง"
            else:
                return "เมื่อครู่"

        except Exception as e:
            logger.warning(f"Time parse error: {str(e)}")
            return "เร็วๆ นี้"

    def _determine_sentiment(self, text: str) -> str:
        """Determine sentiment from article text"""
        text_lower = text.lower()

        bullish_words = ["surge", "rally", "bullish", "gain", "rise", "high", "breakout", "recovery", "growth"]
        bearish_words = ["fall", "drop", "bearish", "loss", "decline", "crash", "pressure", "weak", "sell"]

        bull_count = sum(1 for w in bullish_words if w in text_lower)
        bear_count = sum(1 for w in bearish_words if w in text_lower)

        if bull_count > bear_count:
            return "tag-bull"
        elif bear_count > bull_count:
            return "tag-bear"
        else:
            return "tag-neutral"

    def fetch_all_news(self) -> List[Dict]:
        """Fetch news from sources in priority order: FMP -> Tavily -> Brave (if needed)"""
        logger.info("=" * 50)
        logger.info("🌐 Starting News Agent - Priority: FMP → Tavily → Brave")
        logger.info("=" * 50)

        all_news = []
        min_articles_needed = 10  # If FMP + Tavily gives fewer than this, use Brave

        # Step 1: Fetch FMP first (highest priority)
        logger.info("📡 Step 1: Fetching FMP...")
        fmp_articles = self.fetch_fmp_news()
        all_news.extend(fmp_articles)
        logger.info(f"📊 FMP got {len(fmp_articles)} articles")

        # Step 2: Fetch Tavily second
        logger.info("🌐 Step 2: Fetching Tavily...")
        tavily_articles = self.fetch_tavily_news()
        all_news.extend(tavily_articles)
        logger.info(f"📊 Tavily got {len(tavily_articles)} articles")

        # Step 3: Only use Brave if FMP + Tavily is insufficient
        total_so_far = len(all_news)
        if total_so_far < min_articles_needed:
            logger.info(f"🔍 Step 3: Only {total_so_far} articles - Fetching Brave as backup...")
            brave_articles = self.fetch_brave_news()
            all_news.extend(brave_articles)
            logger.info(f"📊 Brave added {len(brave_articles)} articles")
        else:
            logger.info(f"✅ Have {total_so_far} articles from FMP + Tavily - Skipping Brave")

        # Deduplicate
        unique_news = self._deduplicate(all_news)
        logger.info(f"📊 Total unique articles: {len(unique_news)}")

        # Translate to Thai (parallel for speed)
        logger.info("🌐 Translating articles to Thai...")
        def translate_article(article):
            article["title_th"] = self._translate_to_thai(article["title"])
            article["summary_th"] = self._translate_to_thai(article["summary"][:300] + "..." if len(article["summary"]) > 300 else article["summary"])
            article["time_ago"] = self._format_time_ago(article["publishedAt"])
            article["sentiment"] = self._determine_sentiment(article["title"] + " " + article.get("summary", ""))
            return article

        with ThreadPoolExecutor(max_workers=10) as executor:
            unique_news = list(executor.map(translate_article, unique_news))

        # Sort by recency
        unique_news.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)

        self.news_articles = unique_news
        return unique_news

    def generate_news_html(self, output_path: str = None) -> str:
        """Generate the news.html page"""
        logger.info("📝 Generating news.html...")

        from pathlib import Path
        base_dir = Path(__file__).parent.parent
        if output_path is None:
            output_path = base_dir / "news.html"

        # Build category sections
        categories = {
            "price": {"title": "💰 ราคาทองคำ (Gold Price)", "icon": "💰", "articles": []},
            "fed": {"title": "🏦 นโยบายธนาคารกลางและ Fed", "icon": "🏦", "articles": []},
            "war": {"title": "⚔️ สงครามและภูมิรัฐศาสตร์", "icon": "⚔️", "articles": []},
            "inflation": {"title": "📈 เงินเฟ้อและปัจจัยพื้นฐาน", "icon": "📈", "articles": []},
            "centralbank": {"title": "🏛️ ธนาคารกลางและทองคำสำรอง", "icon": "🏛️", "articles": []}
        }

        for article in self.news_articles:
            cat = article.get("category", "price")
            if cat in categories:
                categories[cat]["articles"].append(article)

        # Count API status - build API status items properly
        fmp_status = "active" if self.api_status['fmp'] else "inactive"
        brave_status = "active" if self.api_status['brave'] else "inactive"
        tavily_status = "active" if self.api_status['tavily'] else "inactive"
        fmp_icon = "✅" if self.api_status['fmp'] else "❌"
        brave_icon = "✅" if self.api_status['brave'] else "❌"
        tavily_icon = "✅" if self.api_status['tavily'] else "❌"

        api_status_items = f'''
                <span class="api-status-item {fmp_status}">FMP {fmp_icon}</span>
                <span class="api-status-item {brave_status}">Brave {brave_icon}</span>
                <span class="api-status-item {tavily_status}">Tavily {tavily_icon}</span>'''

        now = datetime.now()
        date_str = now.strftime("%B %d, %Y")
        time_str = now.strftime("%H:%M GMT+7")

        # Build news sections HTML
        sections_html = ""
        category_tabs_html = '<button class="filter-tab active" data-category="all">📊 ทั้งหมด</button>'

        cat_order = ["price", "fed", "war", "inflation", "centralbank"]
        for cat in cat_order:
            cat_data = categories[cat]
            if cat_data["articles"]:
                category_tabs_html += f'<button class="filter-tab" data-category="{cat}">{cat_data["icon"]} {cat_data["title"].split(" ")[1]}</button>'

                articles_html = ""
                for art in cat_data["articles"][:6]:  # Max 6 per category
                    articles_html += f'''
                <a href="{art['url']}" target="_blank" class="news-card">
                    <div class="news-meta">
                        <span class="news-source">{art['source']}</span>
                        <span class="news-date">{art['time_ago']}</span>
                    </div>
                    <h3 class="news-title">{art['title_th']}</h3>
                    <p class="news-summary">{art['summary_th']}</p>
                    <span class="news-tag {art['sentiment']}">{art['api']}</span>
                </a>'''

                sections_html += f'''
            <section class="section" id="{cat}-section">
                <div class="section-header">
                    <div class="section-icon">{cat_data["icon"]}</div>
                    <div>
                        <h2 class="section-title">{cat_data["title"]}</h2>
                        <p class="section-subtitle">ข่าวล่าสุด {len(cat_data["articles"])} ข่าว</p>
                    </div>
                </div>
                <div class="news-grid">
                    {articles_html}
                </div>
            </section>
                '''

        total_articles = len(self.news_articles)

        html = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📰 Gold News - XAUUSD Trading Hub</title>
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link href="assets/css/style.css" rel="stylesheet">
    <script src="assets/components/ui-components.js" defer></script>
    <script src="assets/js/main.js" defer></script>
</head>
<body>
    <div class="container">
        <!-- Navigation -->
        <nav class="nav">
            <a href="index.html"><span class="icon">📊</span><span class="text">แดชบอร์ด</span></a>
            <a href="daily-briefings.html"><span class="icon">📰</span><span class="text">รายวัน</span></a>
            <a href="economic-calendar.html"><span class="icon">📅</span><span class="text">ปฏิทิน</span></a>
            <a href="gold-analysis.html"><span class="icon">🔍</span><span class="text">วิเคราะห์</span></a>
            <a href="news.html" class="active"><span class="icon">📰</span><span class="text">ข่าว</span></a>
            <a href="weekly-reports.html"><span class="icon">📈</span><span class="text">รายสัปดาห์</span></a>
        </nav>

        <!-- Header -->
        <header class="header">
            <div class="header-top">
                <div class="logo">
                    <div class="logo-icon">📰</div>
                    <div class="logo-text">
                        <h1>ศูนย์ข่าวทองคำ</h1>
                        <p>XAUUSD Trading Hub - ข่าวทองคำล่าสุด</p>
                    </div>
                </div>
                <div class="header-badge">
                    <span class="badge badge-gold">
                        <span class="status-dot gold"></span>
                        อัพเดทสด
                    </span>
                    <span class="badge badge-neutral">
                        {date_str}
                    </span>
                </div>
            </div>
            <div class="update-badge">
                อัพเดทล่าสุด: {time_str} | {total_articles} ข่าวล่าสุด
            </div>
        </header>

        <!-- API Status -->
        <div class="section" style="margin-bottom: 24px;">
            <div class="api-status-bar">
                <span class="api-status-label">🔄 สถานะ API:</span>
                {api_status_items}
                <button class="refresh-btn" onclick="location.reload()">🔄 รีเฟรช</button>
            </div>
        </div>

        <!-- Category Filter -->
        <div class="section" style="margin-bottom: 24px;">
            <div class="filter-tabs">
                {category_tabs_html}
            </div>
        </div>

        {sections_html}

        <!-- Market Sentiment Summary -->
        <section class="section">
            <div class="section-header">
                <div class="section-icon">🎯</div>
                <div>
                    <h2 class="section-title">สรุปความเชื่อมั่นตลาด (Market Sentiment Summary)</h2>
                    <p class="section-subtitle">ภาพรวมความเชื่อมั่นของนักลงทุนจากข่าวล่าสุด</p>
                </div>
            </div>

            <div class="scenario-grid">
                <div class="scenario-item bull">
                    <div class="scenario-title">📈 ปัจจัยบวก (Bullish Factors)</div>
                    <div class="scenario-content">
                        <ul>
                            <li>💰 ดอลลาร์สหรัฐอ่อนตัว</li>
                            <li>🟡 แรงซื้อจากธนาคารกลาง</li>
                            <li>📊 ความตึงเครียดทางภูมิรัฐศาสตร์</li>
                            <li>🎯 เงินเฟ้อขาขึ้น</li>
                        </ul>
                    </div>
                </div>
                <div class="scenario-item bear">
                    <div class="scenario-title">📉 ปัจจัยลบ (Bearish Factors)</div>
                    <div class="scenario-content">
                        <ul>
                            <li>⚔️ สงครามขยายตัว</li>
                            <li>📊 Fed ขึ้นดอกเบี้ย</li>
                            <li>🛢️ ราคาน้ำมันสูง</li>
                            <li>🏦 กำไรทำกำไรหลังขึ้นหนัก</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div style="margin-top: 20px; padding: 16px; background: var(--bg-card-hover); border-radius: 10px;">
                <p style="color: var(--text-secondary);">
                    <strong>📋 สรุป:</strong> ข่าวล่าสุดส่วนใหญ่มองว่าราคาทองยังคงมีแนวโน้มขาขึ้นระยะยาว แต่ในระยะสั้นมีความเสี่ยงจากสงครามและความตึงเครียดทางภูมิรัฐศาสตร์
                    <strong style="color: var(--gold);">แนวรับสำคัญ:</strong> $4,742 | <strong style="color: var(--gold);">แนวต้าน:</strong> $4,917-$4,893
                </p>
            </div>
        </section>

        <!-- Disclaimer -->
        <div class="disclaimer">
            ⚠️ <strong>ข้อจำกัดความรับผิดชอบ:</strong> ข่าวนี้จัดทำเพื่อวัตถุประสงค์เท่านั้น
            การซื้อขาย XAUUSD มีความเสี่ยงสูง ผลการดำเนินงานในอดีตไม่ได้รับประกันผลลัพธ์ในอนาคต
            ควรวิเคราะห์ด้วยตัวเองและปรึกษาที่ปรึกษาทางการเงินที่ได้รับอนุญาตก่อนตัดสินใจซื้อขาย
        </div>

        <!-- Footer -->
        <footer class="footer">
            <div class="footer-logo">🟡</div>
            <p class="footer-text">
                <strong>XAUUSD Trading Hub</strong> | News from FMP API, Brave Search, Tavily | Generated: {date_str} {time_str}
            </p>
            <p class="footer-text" style="margin-top: 8px;">
                <a href="https://github.com/BassSG/xauusd-trading-hub" target="_blank">GitHub</a> |
                <a href="https://BassSG.github.io/xauusd-trading-hub/" target="_blank">Dashboard</a> |
                <a href="economic-calendar.html">Calendar</a>
            </p>
        </footer>
    </div>

    <style>
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}

        .news-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            text-decoration: none;
            color: var(--text-primary);
            transition: all var(--transition-normal);
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .news-card:hover {{
            background: var(--bg-card-hover);
            border-color: rgba(255, 215, 0, 0.3);
            transform: translateY(-3px);
            box-shadow: var(--shadow-gold);
        }}

        .news-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
        }}

        .news-source {{
            color: var(--gold);
            font-weight: 600;
        }}

        .news-date {{
            color: var(--text-muted);
        }}

        .news-title {{
            font-size: 15px;
            font-weight: 600;
            line-height: 1.4;
            color: var(--text-primary);
        }}

        .news-summary {{
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.5;
            flex-grow: 1;
        }}

        .news-tag {{
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 20px;
            display: inline-block;
            width: fit-content;
        }}

        .tag-bull {{
            background: rgba(34, 197, 94, 0.2);
            color: var(--bullish);
        }}

        .tag-bear {{
            background: rgba(239, 68, 68, 0.2);
            color: var(--bearish);
        }}

        .tag-neutral {{
            background: rgba(234, 179, 8, 0.2);
            color: var(--neutral);
        }}

        .filter-tabs {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .filter-tab {{
            padding: 10px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-secondary);
            font-size: 14px;
            cursor: pointer;
            transition: all var(--transition-fast);
        }}

        .filter-tab:hover {{
            background: var(--bg-card-hover);
            color: var(--text-primary);
        }}

        .filter-tab.active {{
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.2) 0%, rgba(255, 215, 0, 0.1) 100%);
            border-color: rgba(255, 215, 0, 0.3);
            color: var(--gold);
        }}

        .api-status-bar {{
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 12px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            flex-wrap: wrap;
        }}

        .api-status-label {{
            font-weight: 600;
            color: var(--text-primary);
        }}

        .api-status-item {{
            font-size: 12px;
            padding: 4px 12px;
            border-radius: 20px;
            background: rgba(239, 68, 68, 0.2);
            color: var(--bearish);
        }}

        .api-status-item.active {{
            background: rgba(34, 197, 94, 0.2);
            color: var(--bullish);
        }}

        .refresh-btn {{
            padding: 8px 16px;
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.2) 0%, rgba(255, 215, 0, 0.1) 100%);
            border: 1px solid rgba(255, 215, 0, 0.3);
            border-radius: 8px;
            color: var(--gold);
            font-size: 14px;
            cursor: pointer;
            margin-left: auto;
            transition: all var(--transition-fast);
        }}

        .refresh-btn:hover {{
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.3) 0%, rgba(255, 215, 0, 0.2) 100%);
        }}
    </style>

    <script>
        // Simple category filter
        document.querySelectorAll('.filter-tab').forEach(tab => {{
            tab.addEventListener('click', () => {{
                // Update active state
                document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                const category = tab.dataset.category;
                const sections = document.querySelectorAll('.section[id]');

                sections.forEach(section => {{
                    if (section.id === 'fed-section' || section.id === 'war-section' ||
                        section.id === 'inflation-section' || section.id === 'price-section' || section.id === 'centralbank-section') {{
                        if (category === 'all') {{
                            section.style.display = 'block';
                        }} else {{
                            const categoryMap = {{
                                'price': 'price-section',
                                'fed': 'fed-section',
                                'war': 'war-section',
                                'inflation': 'inflation-section',
                                'centralbank': 'centralbank-section'
                            }};
                            section.style.display = section.id === categoryMap[category] ? 'block' : 'none';
                        }}
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>'''

        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"✅ news.html generated: {output_path}")
        return str(output_path)

    def save_news_json(self, output_path: str = None) -> str:
        """Save news data as JSON"""
        from pathlib import Path
        base_dir = Path(__file__).parent.parent
        if output_path is None:
            output_path = base_dir / "news_data.json"

        data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "api_status": self.api_status,
            "total_articles": len(self.news_articles),
            "articles": self.news_articles
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ news_data.json saved: {output_path}")
        return str(output_path)

    def upload_to_github(self, file_path: str, repo_path: str = None) -> bool:
        """Upload file to GitHub"""
        if not GITHUB_TOKEN:
            logger.warning("⚠️ No GitHub token - skipping upload")
            return False

        try:
            import base64

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            filename = os.path.basename(file_path)

            # Get current file SHA if exists
            api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{filename}"

            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }

            # Check if file exists
            req = urllib.request.Request(api_url, headers=headers)
            sha = None
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read())
                    sha = data.get("sha")
            except:
                pass

            # Upload file
            data = {
                "message": f"Update {filename} - News Agent ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
                "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')
            }
            if sha:
                data["sha"] = sha

            req = urllib.request.Request(
                api_url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method="PUT"
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                logger.info(f"✅ Uploaded {filename} to GitHub")
                return True

        except Exception as e:
            logger.error(f"❌ GitHub upload failed: {str(e)}")
            return False


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("📰 XAUUSD Trading Hub - NEWS AGENT")
    logger.info("=" * 60)

    agent = NewsAgent()

    # Fetch all news
    agent.fetch_all_news()

    # Generate HTML
    html_path = agent.generate_news_html()

    # Save JSON
    json_path = agent.save_news_json()

    # Upload to GitHub
    agent.upload_to_github(html_path)
    agent.upload_to_github(json_path)

    logger.info("=" * 60)
    logger.info("✅ News Agent completed!")
    logger.info(f"📝 Generated: {html_path}")
    logger.info(f"📊 Data: {json_path}")
    logger.info("=" * 60)

    return agent.news_articles


if __name__ == "__main__":
    main()
