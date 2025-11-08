# generate_sensexy.ps1 - Windows PowerShell Script

Write-Host "======================================"
Write-Host "  SENSEXY BOT - COMPLETE GENERATOR"
Write-Host "======================================"
Write-Host ""

# Your credentials
$BOT_TOKEN = "8531643397:AAHjWOkL71FIFUA0u1rjRX3JTFUL0gYjgOA"
$CHAT_ID = "1225012575"

Write-Host "📝 Creating all bot files with your credentials..."
Write-Host "   Bot Token: $($BOT_TOKEN.Substring(0,20))..."
Write-Host "   Chat ID: $CHAT_ID"
Write-Host ""

# Create requirements.txt
@"
requests==2.31.0
pandas==2.0.3
numpy==1.24.3
yfinance==0.2.18
schedule==1.2.0
python-dotenv==1.0.0
pytz==2023.3
"@ | Out-File -FilePath "requirements.txt" -Encoding UTF8
Write-Host "✅ Created requirements.txt"

# Create .env file
@"
# Telegram Configuration
TELEGRAM_BOT_TOKEN=$BOT_TOKEN
TELEGRAM_CHAT_ID=$CHAT_ID
"@ | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "✅ Created .env with your credentials"

# Create config.py
@'
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Trading Parameters
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
TARGET_PROFIT_PERCENT = 1.0
STOP_LOSS_PERCENT = 0.5
MAX_TRADES = 3
ANALYSIS_INTERVAL = 300  # 5 minutes

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
    'sure', 'fine', 'cool', 'nice', 'do', 'k', 'alright'
]

# Symbol Aliases
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
'@ | Out-File -FilePath "config.py" -Encoding UTF8
Write-Host "✅ Created config.py"

# Create all other Python files...
# [Continue with other files - I'll create a batch file instead for simplicity]

Write-Host ""
Write-Host "Creating batch installer for remaining files..."