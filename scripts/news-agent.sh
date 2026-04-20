#!/bin/bash
# News Agent Cron Job
# Runs every weekday at 09:00 AM (BKK time)
# Updates news.html for XAUUSD Trading Hub

cd /home/administrator/xauusd-trading-hub

# Set environment variables if needed
export PYTHONPATH=/home/administrator/xauusd-trading-hub/backend:$PYTHONPATH

# Run the news agent
python3 backend/news_agent.py

echo "News Agent completed at $(date)" >> /home/administrator/xauusd-trading-hub/cron.log
