import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

VATSIM_URL = "https://data.vatsim.net/v3/vatsim-data.json"

PREFIXES = [
    "LR",
    "LT",
    "ANK"
]

SUFFIXES = [
    "_CTR",
    "_APP",
    "_TWR",
    "_GND",
    "_DEL"
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, json=payload)

def check_vatsim():
    data = requests.get(VATSIM_URL, timeout=20).json()
    controllers = data.get("controllers", [])

    found = []

    for c in controllers:
        callsign = c.get("callsign", "").upper()

        if not any(callsign.startswith(p) for p in PREFIXES):
            continue

        if not any(callsign.endswith(s) for s in SUFFIXES):
            continue

        found.append(
            f"📡 {callsign}\n"
            f"👤 {c.get('name')}\n"
            f"📻 {c.get('frequency')}"
        )

    if found:
        message = (
            "🛫 VATSIM TÜRKİYE SEKTÖR AÇIK\n\n" +
            "\n\n".join(found)
        )
        send_telegram(message)

if __name__ == "__main__":
    check_vatsim()
