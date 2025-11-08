#!/bin/bash

echo "======================================"
echo "  SENSEXY BOT - SETUP INSTALLER"
echo "======================================"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary files
echo "Creating configuration files..."

# Create .env file if not exists
if [ ! -f .env ]; then
    cat > .env << EOL
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
EOL
    echo "✅ Created .env file - Please update with your credentials"
else
    echo "⚠️  .env file already exists"
fi

# Create portfolio.json if not exists
if [ ! -f portfolio.json ]; then
    echo '{"active_trades": {}, "closed_trades": [], "total_pnl": 0}' > portfolio.json
    echo "✅ Created portfolio.json"
fi

# Make main script executable
chmod +x sensexy_bot.py

echo ""
echo "======================================"
echo "  SETUP COMPLETE!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Update .env file with your Telegram credentials"
echo "2. Get Bot Token from @BotFather on Telegram"
echo "3. Get Chat ID by messaging your bot and checking:"
echo "   https://api.telegram.org/bot<YourBOTToken>/getUpdates"
echo "4. Run: source venv/bin/activate"
echo "5. Run: python sensexy_bot.py"
echo ""