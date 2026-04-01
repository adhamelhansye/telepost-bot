import os
import logging
import requests

log = logging.getLogger(__name__)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]  # e.g. @yourchannel or -100...
DISABLE_PREVIEW = os.environ.get("DISABLE_PREVIEW", "true").lower() == "true"
SILENT = os.environ.get("SILENT_POST", "false").lower() == "true"


def post_to_telegram(text: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": DISABLE_PREVIEW,
        "disable_notification": SILENT,
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        data = resp.json()
        if data.get("ok"):
            log.info(f"Posted to Telegram: message_id={data['result']['message_id']}")
            return True
        else:
            log.error(f"Telegram API error: {data.get('description')}")
            return False
    except Exception as e:
        log.error(f"Request to Telegram failed: {e}")
        return False
