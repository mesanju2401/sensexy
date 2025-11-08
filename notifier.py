import requests
import re
from datetime import datetime
import pytz
from config import *

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.ist = pytz.timezone('Asia/Kolkata')
        self.pending_signals = {}
        self.last_update_id = None
        
    def send_message(self, message, parse_mode='HTML'):
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def format_signal_message(self, signal):
        """Format signal message with emojis and structure"""
        emoji_map = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HIGH': '🔥',
            'MEDIUM': '⚡',
            'LOW': '💡'
        }
        
        action_emoji = emoji_map.get(signal['type'], '📊')
        confidence_emoji = emoji_map.get(signal['confidence'], '📈')
        
        message = f"""
{action_emoji} <b>F&O TRADE RECOMMENDATION</b> {action_emoji}
━━━━━━━━━━━━━━━━━━━━━━
📍 <b>Instrument:</b> {signal['symbol']} {signal['option_type']}
💰 <b>Strike Price:</b> ₹{signal['strike_price']:,.0f}
📊 <b>Action:</b> {signal['type']}
💵 <b>Current Price:</b> ₹{signal['current_price']:,.2f}
🎯 <b>Target:</b> ₹{signal['target_price']:,.2f} ({TARGET_PROFIT_PERCENT}%)
🛑 <b>Stop Loss:</b> ₹{signal['stop_loss']:,.2f} ({STOP_LOSS_PERCENT}%)
📏 <b>Lot Size:</b> {signal['lot_size']}
{confidence_emoji} <b>Confidence:</b> {signal['confidence']}
📝 <b>Reason:</b> {signal.get('reason', 'Technical signal')}
━━━━━━━━━━━━━━━━━━━━━━
<i>Reply with: YES/OK/GO/KK or any confirmation</i>
        """
        return message
    
    def format_trade_execution_message(self, trade):
        """Format trade execution confirmation"""
        message = f"""
✅ <b>TRADE EXECUTED SUCCESSFULLY</b> ✅
━━━━━━━━━━━━━━━━━━━━━━
🆔 <b>Trade ID:</b> {trade['id']}
📍 <b>Symbol:</b> {trade['symbol']} {trade['option_type']}
💰 <b>Strike:</b> ₹{trade['strike_price']:,.0f}
📊 <b>Type:</b> {trade['type']}
💵 <b>Entry:</b> ₹{trade['entry_price']:,.2f}
🎯 <b>Target:</b> ₹{trade['target_price']:,.2f}
🛑 <b>Stop Loss:</b> ₹{trade['stop_loss']:,.2f}
📦 <b>Quantity:</b> {trade['quantity']} units
⏰ <b>Time:</b> {datetime.now(self.ist).strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━
<i>Monitoring position for exit...</i>
        """
        return message
    
    def format_trade_close_message(self, trade):
        """Format trade closure message"""
        pnl = trade.get('pnl_amount', 0)
        pnl_percent = trade.get('pnl_percent', 0)
        
        if pnl >= 0:
            emoji = '🟢'
            status = 'PROFIT'
        else:
            emoji = '🔴'
            status = 'LOSS'
        
        message = f"""
{emoji} <b>TRADE CLOSED - {trade.get('exit_reason', 'MANUAL')}</b> {emoji}
━━━━━━━━━━━━━━━━━━━━━━
🆔 <b>Trade ID:</b> {trade['id']}
📍 <b>Symbol:</b> {trade['symbol']} {trade['option_type']}
💵 <b>Entry:</b> ₹{trade['entry_price']:,.2f}
💰 <b>Exit:</b> ₹{trade.get('current_price', trade['entry_price']):,.2f}
━━━━━━━━━━━━━━━━━━━━━━
💹 <b>P&L:</b> ₹{pnl:,.2f}
📊 <b>Return:</b> {pnl_percent:+.2f}%
🏆 <b>Status:</b> {status}
━━━━━━━━━━━━━━━━━━━━━━
        """
        return message
    
    def parse_user_response(self, text):
        """Enhanced parser for user responses"""
        if not text:
            return None
        
        text_lower = text.lower().strip()
        
        # Check for confirmation keywords
        confirmed = False
        for keyword in CONFIRMATION_KEYWORDS:
            if keyword in text_lower:
                confirmed = True
                break
        
        if not confirmed:
            return None
        
        # Parse symbol from response
        parsed_symbol = None
        for alias, symbol in SYMBOL_ALIASES.items():
            if alias in text_lower:
                parsed_symbol = symbol
                break
        
        # Parse option type from response
        parsed_option = None
        for alias, option_type in OPTION_ALIASES.items():
            if alias in text_lower:
                parsed_option = option_type
                break
        
        return {
            'confirmed': True,
            'symbol': parsed_symbol,
            'option_type': parsed_option,
            'raw_text': text
        }
    
    def get_updates(self):
        """Get updates from Telegram"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {}
            if self.last_update_id:
                params['offset'] = self.last_update_id + 1
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('ok') and data.get('result'):
                updates = data['result']
                if updates:
                    self.last_update_id = updates[-1]['update_id']
                return updates
            return []
        except Exception as e:
            print(f"Error getting updates: {e}")
            return []
    
    def process_user_responses(self):
        """Process user responses for pending signals"""
        updates = self.get_updates()
        confirmed_signals = []
        
        for update in updates:
            if 'message' in update and 'text' in update['message']:
                user_text = update['message']['text']
                user_response = self.parse_user_response(user_text)
                
                if user_response and user_response['confirmed']:
                    # Find matching pending signal
                    for signal_id, signal in list(self.pending_signals.items()):
                        # Check if user specified a symbol or just confirmed
                        if user_response['symbol']:
                            if signal['symbol'] == user_response['symbol']:
                                confirmed_signals.append(signal)
                                del self.pending_signals[signal_id]
                                break
                        else:
                            # No specific symbol mentioned, confirm the most recent signal
                            confirmed_signals.append(signal)
                            del self.pending_signals[signal_id]
                            break
        
        return confirmed_signals
    
    def send_portfolio_summary(self, summary):
        """Send portfolio summary message"""
        message = f"""
📊 <b>PORTFOLIO SUMMARY</b> 📊
━━━━━━━━━━━━━━━━━━━━━━
📈 <b>Active Trades:</b> {summary['active_trades']}/{MAX_TRADES}
✅ <b>Closed Trades:</b> {summary['closed_trades']}
💰 <b>Total P&L:</b> ₹{summary['total_pnl']:,.2f}
🎯 <b>Win Rate:</b> {summary['win_rate']:.1f}%
⏰ <b>Updated:</b> {datetime.now(self.ist).strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━
        """
        self.send_message(message)