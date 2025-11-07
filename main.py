#!/usr/bin/env python3
"""
Sensexy - Smart F&O Trading Assistant
Author: Your Name
Version: 1.0.0
"""

import time
import signal
import sys
import logging
from datetime import datetime
import pytz
import yfinance as yf

from config import *
from market_analyzer import MarketAnalyzer
from trade_manager import TradeManager
from notifier import TelegramNotifier
from utils import MarketUtils

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sensexy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Sensexy')

class SensexyBot:
    class SensexyBot:
        def __init__(self):
            self.analyzer = MarketAnalyzer()
            self.trade_manager = TradeManager()
            self.notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
            self.utils = MarketUtils()
            self.ist = pytz.timezone('Asia/Kolkata')
            self.running = True
            self.last_analysis_time = None
            
            logger.info("Sensexy Bot initialized successfully")
            self.send_startup_message()
        
        def send_startup_message(self):
            """Send startup message to Telegram"""
            message = f"""
    🚀 <b>SENSEXY BOT STARTED</b> 🚀
    ━━━━━━━━━━━━━━━━━━━━━━
    🤖 <b>Version:</b> 1.0.0
    📊 <b>Monitoring:</b> SENSEX, NIFTY50, BANKNIFTY
    ⚙️ <b>Settings:</b>
    • Target: {TARGET_PROFIT_PERCENT}%
    • Stop Loss: {STOP_LOSS_PERCENT}%
    • Max Trades: {MAX_TRADES}
    • RSI Levels: {RSI_OVERSOLD}/{RSI_OVERBOUGHT}
    🕒 <b>Time:</b> {datetime.now(self.ist).strftime('%Y-%m-%d %H:%M:%S IST')}
    ━━━━━━━━━━━━━━━━━━━━━━
    <i>Ready to analyze markets!</i>
            """
            self.notifier.send_message(message)
        
        def get_current_prices(self):
            """Get current prices for all symbols"""
            prices = {}
            for symbol_name, symbol_config in SYMBOLS.items():
                try:
                    ticker = yf.Ticker(symbol_config['ticker'])
                    data = ticker.history(period='1d', interval='1m')
                    if not data.empty:
                        prices[symbol_name] = data['Close'].iloc[-1]
                except Exception as e:
                    logger.error(f"Error fetching price for {symbol_name}: {e}")
            return prices
        
        def analyze_markets(self):
            """Analyze markets and generate signals"""
            if not self.utils.is_market_open():
                return
            
            logger.info("Starting market analysis...")
            
            # Get signals from analyzer
            signals = self.analyzer.analyze_all_symbols()
            
            if signals:
                for signal in signals:
                    # Store signal as pending and send to Telegram
                    signal_id = f"SIG_{datetime.now().strftime('%H%M%S')}"
                    self.notifier.pending_signals[signal_id] = signal
                    
                    # Send signal message
                    message = self.notifier.format_signal_message(signal)
                    self.notifier.send_message(message)
                    
                    logger.info(f"Signal sent for {signal['symbol']} {signal['option_type']}")
            
            # Update existing trades
            current_prices = self.get_current_prices()
            closed_trades = self.trade_manager.update_trade_prices(current_prices)
            
            # Send notifications for closed trades
            for trade in closed_trades:
                message = self.notifier.format_trade_close_message(trade)
                self.notifier.send_message(message)
                logger.info(f"Trade {trade['id']} closed: {trade['exit_reason']}")
        
        def process_confirmations(self):
            """Process user confirmations and execute trades"""
            confirmed_signals = self.notifier.process_user_responses()
            
            for signal in confirmed_signals:
                # Create trade
                trade, error = self.trade_manager.create_trade(signal)
                
                if trade:
                    # Send execution confirmation
                    message = self.notifier.format_trade_execution_message(trade)
                    self.notifier.send_message(message)
                    logger.info(f"Trade executed: {trade['id']}")
                else:
                    # Send error message
                    error_msg = f"❌ <b>Trade Execution Failed</b>\n{error}"
                    self.notifier.send_message(error_msg)
                    logger.error(f"Trade execution failed: {error}")
        
        def send_daily_summary(self):
            """Send daily portfolio summary"""
            summary = self.trade_manager.get_portfolio_summary()
            self.notifier.send_portfolio_summary(summary)
            logger.info("Daily summary sent")
        
        def run_analysis_cycle(self):
            """Run a complete analysis cycle"""
            try:
                # Check market status
                if not self.utils.is_market_open():
                    return
                
                # Run analysis
                self.analyze_markets()
                
                # Process any pending confirmations
                self.process_confirmations()
                
                # Send periodic summary (every hour)
                current_time = datetime.now(self.ist)
                if current_time.minute == 0:  # On the hour
                    self.send_daily_summary()
                
            except Exception as e:
                logger.error(f"Error in analysis cycle: {e}")
                error_msg = f"⚠️ <b>Analysis Error</b>\n{str(e)[:200]}"
                self.notifier.send_message(error_msg)
        
        def signal_handler(self, signum, frame):
            """Handle shutdown signals"""
            logger.info("Shutdown signal received")
            self.running = False
            self.shutdown()
        
        def shutdown(self):
            """Clean shutdown"""
            message = f"""
    🛑 <b>SENSEXY BOT STOPPING</b> 🛑
    ━━━━━━━━━━━━━━━━━━━━━━
    📊 Final Portfolio Summary:
    """
            summary = self.trade_manager.get_portfolio_summary()
            message += f"""
    • Active Trades: {summary['active_trades']}
    • Total P&L: ₹{summary['total_pnl']:,.2f}
    • Win Rate: {summary['win_rate']:.1f}%
    ━━━━━━━━━━━━━━━━━━━━━━
    <i>Bot stopped at {datetime.now(self.ist).strftime('%H:%M:%S IST')}</i>
            """
            self.notifier.send_message(message)
            logger.info("Sensexy Bot stopped")
            sys.exit(0)
        
        def run(self):
            """Main bot loop"""
            # Setup signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            logger.info("Starting main bot loop...")
            
            while self.running:
                try:
                    # Wait for market to open if closed
                    if not self.utils.is_market_open():
                        next_open = self.utils.get_next_market_open()
                        wait_msg = f"""
    ⏸️ <b>Market Closed</b>
    Next opening: {next_open.strftime('%Y-%m-%d %H:%M:%S IST')}
    Bot waiting for market to open...
                        """
                        self.notifier.send_message(wait_msg)
                        
                        while not self.utils.is_market_open() and self.running:
                            time.sleep(60)  # Check every minute
                            # Process any pending confirmations even when market is closed
                            self.process_confirmations()
                    
                    # Market is open, run analysis
                    if self.running:
                        self.run_analysis_cycle()
                        time.sleep(ANALYSIS_INTERVAL)  # Wait 5 minutes
                    
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    time.sleep(60)  # Wait a minute before retrying

    def main():
        """Main entry point"""
        print("""
        ╔════════════════════════════════════════╗
        ║     SENSEXY - Smart F&O Trading Bot   ║
        ║         Version 1.0.0                  ║
        ╔════════════════════════════════════════╗
        """)
        
        # Check configuration
        if TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
            print("❌ Please configure your Telegram Bot Token in config.py or .env file")
            sys.exit(1)
        
        if TELEGRAM_CHAT_ID == 'YOUR_CHAT_ID_HERE':
            print("❌ Please configure your Telegram Chat ID in config.py or .env file")
            sys.exit(1)
        
        # Start bot
        bot = SensexyBot()
        bot.run()

    if __name__ == "__main__":
        main()