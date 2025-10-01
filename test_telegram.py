import httpx, os
from dotenv import dotenv_values
cfg = dotenv_values(".env")
bot, chat = cfg["BOT_TOKEN"], cfg["CHAT_ID"]
with httpx.Client(timeout=10) as c:
    r = c.get(f"https://api.telegram.org/bot{bot}/sendMessage",
              params={"chat_id": chat, "text": "Test from bot"})
    r.raise_for_status()
print("OK")