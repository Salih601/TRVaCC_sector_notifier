import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

VATSIM_URL = "https://data.vatsim.net/v3/vatsim-data.json"

KEYWORDS = [
    "LT",
    "ANK"
]

SUFFIXES = [
    "_CTR",
    "_APP"
    "_TWR"
    "_GND"
    "_DEL"
]

notified = set()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, json=payload)

def check_vatsim():
    data = requests.get(VATSIM_URL).json()
    controllers = data.get("controllers", [])

    for c in controllers:
        callsign = c.get("callsign", "")
        upper = callsign.upper()

        if not any(upper.startswith(k) for k in KEYWORDS):
            continue

        if not any(upper.endswith(s) for s in SUFFIXES):
            continue

        if upper not in notified:
            msg = (
                f"🛫 VATSIM TÜRKİYE SEKTÖR AÇILDI\n\n"
                f"📡 Callsign: {callsign}\n"
                f"👤 ATC: {c.get('name')}\n"
                f"📻 Frequency: {c.get('frequency')}"
            )
            send_telegram(msg)
            notified.add(upper)

if __name__ == "__main__":
    check_vatsim()
