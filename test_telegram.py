import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

url  = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {
    "chat_id": CHAT_ID,
    "text":    "CyberSec Feed Agent is online. Telegram alerts working.",
    "parse_mode": "HTML"
}

response = requests.post(url, data=data)
print("Status:", response.status_code)
print("Response:", response.json())