import json
import os
from datetime import datetime
import uuid
import pytz
from config import *

class TradeManager:
    def __init__(self):
        self.portfolio_file = 'portfolio.json'
        self.ist = pytz.timezone('Asia/Kolkata')
        self.load_portfolio()
        
    def load_portfolio(self):
        """Load existing portfolio from file"""
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r') as f:
                    self.portfolio = json.load(f)
            except:
                self.portfolio = {'active_trades': {}, 'closed_trades': [], 'total_pnl': 0}
        else:
            self.portfolio = {'active_trades': {}, 'closed_trades': [], 'total_pnl': 0}
    
    def save_portfolio(self):
        """Save portfolio to file"""
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(self.portfolio, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving portfolio: {e}")
    
    def create_trade(self, signal):
        """Create a new trade entry"""
        if len(self.portfolio['active_trades']) >= MAX_TRADES:
            return None, "Maximum trades limit reached"
        
        trade_id = f"TRADE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        trade = {
            'id': trade_id,
            'symbol': signal['symbol'],
            'type': signal['type'],
            'option_type': signal['option_type'],
            'strike_price': signal['strike_price'],
            'entry_price': signal['current_price'],
            'target_price': signal['target_price'],
            'stop_loss': signal['stop_loss'],
            'lot_size': signal['lot_size'],
            'quantity': signal['lot_size'],
            'entry_time': datetime.now(self.ist).isoformat(),
            'status': 'ACTIVE',
            'reason': signal.get('reason', ''),
            'confidence': signal.get('confidence', 'MEDIUM')
        }
        
        self.portfolio['active_trades'][trade_id] = trade
        self.save_portfolio()
        
        return trade, None
    
    def update_trade_prices(self, current_prices):
        """Update current prices and check for exits"""
        trades_to_close = []
        
        for trade_id, trade in self.portfolio['active_trades'].items():
            if trade['symbol'] in current_prices:
                current_price = current_prices[trade['symbol']]
                trade['current_price'] = current_price
                
                # Calculate P&L
                if trade['type'] == 'BUY':
                    pnl_percent = ((current_price - trade['entry_price']) / 
                                  trade['entry_price']) * 100
                else:  # SELL
                    pnl_percent = ((trade['entry_price'] - current_price) / 
                                  trade['entry_price']) * 100
                
                trade['pnl_percent'] = pnl_percent
                trade['pnl_amount'] = (pnl_percent / 100) * trade['entry_price'] * trade['quantity']
                
                # Check exit conditions
                if trade['type'] == 'BUY':
                    if current_price >= trade['target_price']:
                        trades_to_close.append((trade_id, 'TARGET_HIT', pnl_percent))
                    elif current_price <= trade['stop_loss']:
                        trades_to_close.append((trade_id, 'STOP_LOSS_HIT', pnl_percent))
                else:  # SELL
                    if current_price <= trade['target_price']:
                        trades_to_close.append((trade_id, 'TARGET_HIT', pnl_percent))
                    elif current_price >= trade['stop_loss']:
                        trades_to_close.append((trade_id, 'STOP_LOSS_HIT', pnl_percent))
        
        # Close trades that hit targets
        closed_trades = []
        for trade_id, reason, pnl in trades_to_close:
            closed_trade = self.close_trade(trade_id, reason)
            if closed_trade:
                closed_trades.append(closed_trade)
        
        self.save_portfolio()
        return closed_trades
    
    def close_trade(self, trade_id, reason='MANUAL'):
        """Close an active trade"""
        if trade_id not in self.portfolio['active_trades']:
            return None
        
        trade = self.portfolio['active_trades'][trade_id]
        trade['exit_time'] = datetime.now(self.ist).isoformat()
        trade['exit_reason'] = reason
        trade['status'] = 'CLOSED'
        
        # Calculate final P&L
        if 'pnl_amount' in trade:
            self.portfolio['total_pnl'] += trade['pnl_amount']
        
        # Move to closed trades
        self.portfolio['closed_trades'].append(trade)
        del self.portfolio['active_trades'][trade_id]
        
        self.save_portfolio()
        return trade
    
    def get_active_trades(self):
        """Get all active trades"""
        return self.portfolio['active_trades']
    
    def get_portfolio_summary(self):
        """Get portfolio summary"""
        active_count = len(self.portfolio['active_trades'])
        total_pnl = self.portfolio['total_pnl']
        closed_count = len(self.portfolio['closed_trades'])
        
        # Calculate win rate
        winning_trades = [t for t in self.portfolio['closed_trades'] 
                         if t.get('pnl_percent', 0) > 0]
        win_rate = (len(winning_trades) / closed_count * 100) if closed_count > 0 else 0
        
        return {
            'active_trades': active_count,
            'closed_trades': closed_count,
            'total_pnl': total_pnl,
            'win_rate': win_rate
        }