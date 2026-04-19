#!/bin/bash
# Cron Setup Script for XAUUSD Trading Hub
# Run this script to set up automatic daily updates

echo "🔧 Setting up cron jobs for XAUUSD Trading Hub..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/update_data.py"

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.6+"
    exit 1
fi

# Create log directory
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# Cron schedule times (UTC)
# 06:00 UTC = 13:00 Bangkok time (UTC+7)
# 08:00 UTC = 15:00 Bangkok time (UTC+7)

echo ""
echo "📅 Current cron jobs:"
crontab -l 2>/dev/null | grep -i xauusd || echo "   (none)"

echo ""
echo "🕐 Available schedules:"
echo "   1. Daily at 06:00 UTC (13:00 Bangkok) - Recommended for morning briefing"
echo "   2. Daily at 08:00 UTC (15:00 Bangkok) - Alternative timing"
echo "   3. Custom schedule"
echo ""

read -p "Select schedule (1/2/3) [default: 1]: " choice
choice=${choice:-1}

case $choice in
    1)
        CRON_TIME="0 6 * * *"
        CRON_DESC="Daily at 06:00 UTC"
        ;;
    2)
        CRON_TIME="0 8 * * *"
        CRON_DESC="Daily at 08:00 UTC"
        ;;
    3)
        read -p "Enter cron schedule (e.g., '0 6 * * 1-5' for weekdays at 6 AM): " CRON_TIME
        CRON_DESC="Custom: $CRON_TIME"
        ;;
    *)
        CRON_TIME="0 6 * * *"
        CRON_DESC="Daily at 06:00 UTC"
        ;;
esac

# Build cron command
CRON_CMD="cd $SCRIPT_DIR && python3 update_data.py >> $LOG_DIR/cron.log 2>&1"

# Create the cron entry
CRON_ENTRY="$CRON_TIME $CRON_CMD"

# Remove any existing XAUUSD cron jobs first
crontab -l 2>/dev/null | grep -v "xauusd" | grep -v "update_data.py" > /tmp/current_cron

# Add new cron job
echo "$CRON_ENTRY" >> /tmp/current_cron

# Install new crontab
crontab /tmp/current_cron
rm /tmp/current_cron

echo ""
echo "✅ Cron job installed successfully!"
echo ""
echo "📋 Details:"
echo "   Schedule: $CRON_DESC"
echo "   Command: $CRON_CMD"
echo "   Log file: $LOG_DIR/cron.log"
echo ""

# Test run
echo "🧪 Running test update..."
cd "$SCRIPT_DIR"
python3 update_data.py --no-push

echo ""
echo "📊 To view logs: tail -f $LOG_DIR/cron.log"
echo "📊 To remove cron: crontab -e and delete the xauusd line"
