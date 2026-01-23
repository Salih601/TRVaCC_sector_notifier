import requests
import os
import json

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

STATE_FILE = "last_state.txt"

VALID_SUFFIXES = ("_CTR", "_APP", "_TWR", "_GND", "_DEL")
TURKEY_PREFIXES = ("ANK_", "IST_","LT_")

VATSIM_DATA_URL = "https://data.vatsim.net/v3/vatsim-data.json"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)


def is_turkey_sector(callsign: str) -> bool:
    return callsign.startswith(TURKEY_PREFIXES) and callsign.endswith(VALID_SUFFIXES)


def get_online_sectors():
    data = requests.get(VATSIM_DATA_URL, timeout=15).json()
    controllers = data.get("controllers", [])

    sectors = {}

    for c in controllers:
        callsign = c["callsign"]
        if is_turkey_sector(callsign):
            sectors[callsign] = {
                "frequency": c.get("frequency", "—"),
                "name": c.get("name", "Unknown")
            }

    return sectors


def load_last_state():
    if not os.path.exists(STATE_FILE):
        return {}

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def main():
    previous = load_last_state()
    current = get_online_sectors()

    opened = current.keys() - previous.keys()
    closed = previous.keys() - current.keys()

    for s in opened:
        info = current[s]
        send_telegram(
            "<b>VATSIM Turkey sectors are now online.</b>\n\n"
            f"{s}\n"
            f"{info['frequency']} • {info['name']}"
        )

    for s in closed:
        info = previous[s]
        send_telegram(
            "<b>VATSIM Turkey sector has gone offline.</b>\n\n"
            f"{s}\n"
            f"{info['frequency']} • {info['name']}"
        )

    save_state(current)


if __name__ == "__main__":
    main()
