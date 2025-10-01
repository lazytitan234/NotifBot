#get dependencies
import json, time, random
from dotenv import dotenv_values
import httpx
from playwright.sync_api import sync_playwright

#load and set configs
cfg = dotenv_values(".env")  
URL = cfg.get("TARGET_URL", "https://fixr.co/organiser/OUISC?lang=en-US")
BOT = cfg.get("BOT_TOKEN", "")
CHAT = cfg.get("CHAT_ID", "")
STATE_FILE = cfg.get("STATE_FILE", ".ouisc_state.json")
DEFAULT_INTERVAL = 60 
NO_EVENTS_TEXT = "Currently no events"

#various helper functions
def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"was_no_events": True}
    
def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def send_telegram(msg: str):
    if not (BOT and CHAT):
        return
    with httpx.Client(timeout=20) as client:
        client.get(
            f"https://api.telegram.org/bot{BOT}/sendMessage",
            params={"chat_id": CHAT, "text": msg, "parse_mode": "HTML"},
        )

def page_has_no_events(page) -> bool:
    page.goto(URL, wait_until="networkidle")
    text = page.locator("body").inner_text()
    return NO_EVENTS_TEXT.lower() in text.lower()

def run_once():
    state = load_state()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(
            locale="en-GB",
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/125.0.0.0 Safari/537.36"),
        )
        page = context.new_page()
        try:
            no_events = page_has_no_events(page)
        finally:
            context.close()
            browser.close()

    if state.get("was_no_events", True) and not no_events:
        send_telegram("OUISC: events just appeared on FIXR — go check!")
    state["was_no_events"] = no_events
    save_state(state)

if __name__ == "__main__":
    while True:
        run_once()
        time.sleep(DEFAULT_INTERVAL + 10 * random.random())
        