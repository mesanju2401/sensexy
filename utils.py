import pytz
from datetime import datetime, time
import schedule
import time as time_module

class MarketUtils:
    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
    
    def is_market_open(self):
        """Check if market is open"""
        now = datetime.now(self.ist)
        
        # Check if weekday (Monday = 0, Sunday = 6)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check market hours
        market_open = time(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE)
        market_close = time(MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE)
        current_time = now.time()
        
        return market_open <= current_time <= market_close
    
    def get_next_market_open(self):
        """Get next market opening time"""
        now = datetime.now(self.ist)
        
        # If it's a weekday and before market open
        if now.weekday() < 5:
            next_open = now.replace(hour=MARKET_OPEN_HOUR, 
                                   minute=MARKET_OPEN_MINUTE, 
                                   second=0, 
                                   microsecond=0)
            if now.time() < time(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE):
                return next_open
        
        # Find next weekday
        days_ahead = 1
        while True:
            next_day = now + timedelta(days=days_ahead)
            if next_day.weekday() < 5:
                return next_day.replace(hour=MARKET_OPEN_HOUR, 
                                      minute=MARKET_OPEN_MINUTE, 
                                      second=0, 
                                      microsecond=0)
            days_ahead += 1
    
    def wait_for_market(self):
        """Wait for market to open"""
        while not self.is_market_open():
            next_open = self.get_next_market_open()
            wait_time = (next_open - datetime.now(self.ist)).total_seconds()
            
            if wait_time > 3600:  # More than 1 hour
                print(f"Market closed. Next opening: {next_open.strftime('%Y-%m-%d %H:%M:%S IST')}")
                time_module.sleep(3600)  # Check every hour
            else:
                print(f"Market opening in {int(wait_time)} seconds...")
                time_module.sleep(60)  # Check every minute