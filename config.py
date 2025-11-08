import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8531643397:AAHjWOkL71FIFUA0u1rjRX3JTFUL0gYjgOA')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '1225012575')

# Trading Parameters
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
TARGET_PROFIT_PERCENT = 1.0
STOP_LOSS_PERCENT = 0.5
MAX_TRADES = 3
ANALYSIS_INTERVAL = 300  # 5 minutes in seconds

# Market Hours (IST)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30

# Symbols Configuration
SYMBOLS = {
    'SENSEX': {
        'ticker': '^BSESN',
        'name': 'SENSEX',
        'lot_size': 10,
        'strike_step': 100
    },
    'NIFTY50': {
        'ticker': '^NSEI',
        'name': 'NIFTY50',
        'lot_size': 50,
        'strike_step': 50
    },
    'BANKNIFTY': {
        'ticker': '^NSEBANK',
        'name': 'BANKNIFTY',
        'lot_size': 15,
        'strike_step': 100
    }
}

# Confirmation Keywords
CONFIRMATION_KEYWORDS = [
    'yes', 'ok', 'okay', 'kk', 'oo', 'go', 'do it', 'execute',
    'buy', 'sell', 'confirm', 'approve', 'agree', 'accept',
    'go ahead', 'proceed', "let's go", 'yep', 'yup', 'ya',
    'sure', 'fine', 'cool', 'nice', 'do', 'k', 'alright',
    'certainly', 'absolutely', 'definitely', 'positive', 'affirmative'
]

# Symbol Aliases for parsing
SYMBOL_ALIASES = {
    'banknifty': 'BANKNIFTY',
    'bnf': 'BANKNIFTY',
    'bank': 'BANKNIFTY',
    'nifty': 'NIFTY50',
    'nifty50': 'NIFTY50',
    'nf': 'NIFTY50',
    'sensex': 'SENSEX',
    'bse': 'SENSEX'
}

# Option Type Aliases
OPTION_ALIASES = {
    'call': 'CALL',
    'ce': 'CALL',
    'put': 'PUT',
    'pe': 'PUT'
}