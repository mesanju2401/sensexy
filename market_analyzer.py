import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from config import *

class MarketAnalyzer:
    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
        self.signals_cache = {}
        self.last_signal_time = {}
        
    def fetch_data(self, symbol, period='5d', interval='5m'):
        """Fetch market data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def calculate_rsi(self, data, period=14):
        """Calculate Relative Strength Index"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_moving_averages(self, data):
        """Calculate multiple moving averages"""
        ma_periods = [5, 20, 50]
        ma_data = {}
        for period in ma_periods:
            ma_data[f'MA{period}'] = data['Close'].rolling(window=period).mean()
        return ma_data
    
    def calculate_support_resistance(self, data, period=20):
        """Calculate support and resistance levels"""
        support = data['Low'].rolling(window=period).min()
        resistance = data['High'].rolling(window=period).max()
        return support.iloc[-1], resistance.iloc[-1]
    
    def detect_crossover(self, ma_data):
        """Detect golden cross and death cross"""
        if len(ma_data['MA5']) < 2:
            return None
            
        # Golden Cross: Short MA crosses above Long MA
        if (ma_data['MA5'].iloc[-2] <= ma_data['MA20'].iloc[-2] and 
            ma_data['MA5'].iloc[-1] > ma_data['MA20'].iloc[-1]):
            return 'GOLDEN_CROSS'
        
        # Death Cross: Short MA crosses below Long MA
        if (ma_data['MA5'].iloc[-2] >= ma_data['MA20'].iloc[-2] and 
            ma_data['MA5'].iloc[-1] < ma_data['MA20'].iloc[-1]):
            return 'DEATH_CROSS'
        
        return None
    
    def calculate_momentum(self, data):
        """Calculate price momentum"""
        if len(data) < 2:
            return 0
        price_change = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / 
                       data['Close'].iloc[-2]) * 100
        return price_change
    
    def generate_signal(self, symbol_config):
        """Generate trading signal based on technical indicators"""
        symbol = symbol_config['ticker']
        name = symbol_config['name']
        
        # Check if we recently sent a signal
        current_time = datetime.now(self.ist)
        if name in self.last_signal_time:
            time_diff = (current_time - self.last_signal_time[name]).seconds
            if time_diff < 600:  # 10 minute cooldown
                return None
        
        # Fetch market data
        data = self.fetch_data(symbol)
        if data is None or len(data) < 50:
            return None
        
        # Calculate indicators
        rsi = self.calculate_rsi(data)
        ma_data = self.calculate_moving_averages(data)
        support, resistance = self.calculate_support_resistance(data)
        crossover = self.detect_crossover(ma_data)
        momentum = self.calculate_momentum(data)
        
        current_price = data['Close'].iloc[-1]
        current_rsi = rsi.iloc[-1]
        volume_surge = data['Volume'].iloc[-1] > data['Volume'].mean() * 1.5
        
        # Signal generation logic
        signal = {
            'symbol': name,
            'current_price': current_price,
            'rsi': current_rsi,
            'momentum': momentum,
            'timestamp': current_time,
            'confidence': 'LOW'
        }
        
        # Strong BUY signal conditions
        if current_rsi < RSI_OVERSOLD and (crossover == 'GOLDEN_CROSS' or momentum > 0.5):
            signal['type'] = 'BUY'
            signal['option_type'] = 'CALL'
            signal['confidence'] = 'HIGH'
            signal['reason'] = f"RSI oversold ({current_rsi:.1f}) + Bullish momentum"
        
        # Moderate BUY signal
        elif current_rsi < 40 and current_price < support * 1.01:
            signal['type'] = 'BUY'
            signal['option_type'] = 'CALL'
            signal['confidence'] = 'MEDIUM'
            signal['reason'] = f"Near support level + RSI low ({current_rsi:.1f})"
        
        # Strong SELL signal conditions
        elif current_rsi > RSI_OVERBOUGHT and (crossover == 'DEATH_CROSS' or momentum < -0.5):
            signal['type'] = 'SELL'
            signal['option_type'] = 'PUT'
            signal['confidence'] = 'HIGH'
            signal['reason'] = f"RSI overbought ({current_rsi:.1f}) + Bearish momentum"
        
        # Moderate SELL signal
        elif current_rsi > 60 and current_price > resistance * 0.99:
            signal['type'] = 'SELL'
            signal['option_type'] = 'PUT'
            signal['confidence'] = 'MEDIUM'
            signal['reason'] = f"Near resistance level + RSI high ({current_rsi:.1f})"
        
        # Volume-based signal
        elif volume_surge and abs(momentum) > 1:
            signal['type'] = 'BUY' if momentum > 0 else 'SELL'
            signal['option_type'] = 'CALL' if momentum > 0 else 'PUT'
            signal['confidence'] = 'MEDIUM'
            signal['reason'] = f"Volume surge + {abs(momentum):.1f}% price move"
        else:
            return None
        
        # Calculate strike price and targets
        signal['strike_price'] = self.calculate_strike_price(current_price, 
                                                            symbol_config['strike_step'])
        signal['target_price'] = current_price * (1 + TARGET_PROFIT_PERCENT/100)
        signal['stop_loss'] = current_price * (1 - STOP_LOSS_PERCENT/100)
        signal['lot_size'] = symbol_config['lot_size']
        
        self.last_signal_time[name] = current_time
        return signal
    
    def calculate_strike_price(self, current_price, strike_step):
        """Calculate nearest strike price"""
        return round(current_price / strike_step) * strike_step
    
    def analyze_all_symbols(self):
        """Analyze all configured symbols"""
        signals = []
        for symbol_name, symbol_config in SYMBOLS.items():
            signal = self.generate_signal(symbol_config)
            if signal:
                signals.append(signal)
        return signals