# XAUUSD Trading Hub Backend

Backend Integration Agent สำหรับ XAUUSD Trading Hub - รับผิดชอบดึงข้อมูลอัตโนมัติจาก APIs ต่างๆ

## โครงสร้างไฟล์

```
backend/
├── __init__.py           # Package init
├── config.py             # Configuration & API Keys
├── data_fetcher.py       # FMP API integration
├── indicators.py         # Technical indicators calculator
├── sentiment.py          # Brave Search & Travily integration
├── economic_calendar.py  # Economic calendar fetcher
├── main.py               # Main orchestrator
├── update_data.py        # CLI update script
├── api.py                # FastAPI server
├── setup_cron.sh         # Cron job setup script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## APIs ที่ใช้

| API | Purpose | Key |
|-----|---------|-----|
| FMP | Gold price, historical data, economic calendar | `WhZvG1WwRoLOE0vJQGsiS9b5XqTft5rK` |
| Brave Search | News aggregation | `BSAgig-hxX7rPYozDfWr-D1T2xqbVzK` |
| Travily | Additional market data | `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` |

## Installation

```bash
cd xauusd-trading-hub/backend
pip install -r requirements.txt
```

## Usage

### Update ข้อมูลทั้งหมด
```bash
python update_data.py
```

### Update เฉพาะส่วน
```bash
python update_data.py --data        # ราคาทอง
python update_data.py --indicators  # Indicators
python update_data.py --sentiment   # Sentiment
python update_data.py --calendar    # Economic Calendar
python update_data.py --briefing    # Daily Briefing
```

### รัน API Server
```bash
pip install fastapi uvicorn
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### ตั้งค่า Cron Job (อัพเดทอัตโนมัติทุกเช้า)
```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

## Output Files

| File | Description |
|------|-------------|
| `gold-analysis/data.json` | ข้อมูลราคาทอง, MA, Volatility |
| `gold-analysis/indicators.json` | RSI, MACD, Support/Resistance |
| `gold-analysis/sentiment.json` | Market sentiment จากข่าว |
| `gold-analysis/fallback.json` | Fallback data เมื่อ API ล่ม |
| `economic-calendar/upcoming.json` | ปฏิทินเศรษฐกิจ |
| `daily-briefings/YYYY-MM-DD-daily-briefing.md` | รายงานประจำวัน |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/gold-price` | GET | ข้อมูลราคาทอง |
| `/api/indicators` | GET | Technical indicators |
| `/api/sentiment` | GET | Market sentiment |
| `/api/economic-calendar` | GET | Economic calendar |
| `/api/dashboard` | GET | ข้อมูลทั้งหมดรวม |
| `/api/history` | GET | Historical prices |

## Error Handling

- **Fallback Data**: เมื่อ API ล่ม จะใช้ข้อมูลจาก `fallback.json`
- **Retry Logic**: มี retry mechanism ในการเรียก API
- **Logging**: ทุก operation มี logging

## Cron Schedule

เวลาเริ่มต้น: 06:00 UTC (13:00 Bangkok)
- สามารถปรับเปลี่ยนได้ใน `setup_cron.sh`

## การติดตั้ง Cron Job

```bash
# 1. รัน setup script
./setup_cron.sh

# 2. เลือก schedule (1 = 06:00 UTC, 2 = 08:00 UTC, 3 = custom)

# 3. ตรวจสอบ cron job
crontab -l

# 4. ดู logs
tail -f logs/cron.log
```

## GitHub Integration

Script จะ auto-commit และ push ขึ้น GitHub ทุกครั้งที่ run:
- Repository: `BassSG/xauusd-trading-hub`
- Branch: `main`
- Commit message format: `🔄 Auto-update: components (timestamp)`

## License

MIT
