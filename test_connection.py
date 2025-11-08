import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Your credentials
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8531643397:AAHjWOkL71FIFUA0u1rjRX3JTFUL0gYjgOA')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '1225012575')

print(f"🔧 Testing Sensexy Bot Connection...")
print(f"📡 Bot Token: {BOT_TOKEN[:15]}...")
print(f"👤 Chat ID: {CHAT_ID}")

# Send test message
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    'chat_id': CHAT_ID,
    'text': '''
🚀 <b>SENSEXY BOT INITIALIZED</b> 🚀
━━━━━━━━━━━━━━━━━━━━━━
✅ Bot Token: Verified
✅ Chat ID: 1225012575
✅ Connection: Successful
━━━━━━━━━━━━━━━━━━━━━━
🔍 Monitoring: SENSEX, NIFTY50, BANKNIFTY
📊 Targets: 1% Profit | 0.5% Stop Loss
⚡ Analysis: Every 5 minutes
━━━━━━━━━━━━━━━━━━━━━━
<i>Ready to start trading analysis!</i>
    ''',
    'parse_mode': 'HTML'
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("✅ SUCCESS! Check your Telegram for the test message.")
    print("🎉 Your bot is ready to use!")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"Details: {response.text}")