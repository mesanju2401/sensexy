from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from config import (
    MARKET_OPEN_HOUR,
    MARKET_OPEN_MINUTE,
    MARKET_CLOSE_HOUR,
    MARKET_CLOSE_MINUTE
)
import time as time_module


class MarketUtils:
    def __init__(self):
        self.ist = ZoneInfo("Asia/Kolkata")
    
    def is_market_open(self):
        now = datetime.now(self.ist)

        if now.weekday() >= 5:
            return False
        
        market_open = time(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE)
        market_close = time(MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE)
        current_time = now.time()
        
        return market_open <= current_time <= market_close
    
    def get_next_market_open(self):
        now = datetime.now(self.ist)
        
        if now.weekday() < 5:
            next_open = now.replace(
                hour=MARKET_OPEN_HOUR,
                minute=MARKET_OPEN_MINUTE,
                second=0,
                microsecond=0
            )
            if now.time() < time(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE):
                return next_open
        
        days_ahead = 1
        while True:
            next_day = now + timedelta(days=days_ahead)
            if next_day.weekday() < 5:
                return next_day.replace(
                    hour=MARKET_OPEN_HOUR,
                    minute=MARKET_OPEN_MINUTE,
                    second=0,
                    microsecond=0
                )
            days_ahead += 1
    
    def wait_for_market(self):
        while not self.is_market_open():
            next_open = self.get_next_market_open()
            wait_time = (next_open - datetime.now(self.ist)).total_seconds()
            
            if wait_time > 3600:
                print(f"Market closed. Next opening: {next_open.strftime('%Y-%m-%d %H:%M:%S IST')}")
                time_module.sleep(3600)
            else:
                print(f"Market opening in {int(wait_time)} seconds...")
                time_module.sleep(60)
