import requests
import os
import time

VATSIM_DATA_URL = "https://data.vatsim.net/v3/vatsim-data.json"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Daha önce bildirilen sektörleri tutmak için
STATE_FILE = "last_state.txt"

# Takip edilecek sektör anahtarları
KEYWORDS = [
    "LT", "ANK"
]

SUFFIXES = [
    "CTR", "APP", "TWR", "GND", "DEL"
]


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)


def load_last_state():
    try:
        with open(STATE_FILE, "r") as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()


def save_last_state(state):
    with open(STATE_FILE, "w") as f:
        for s in state:
            f.write(s + "\n")


def sector_matches(callsign):
    callsign = callsign.upper()

    if not any(k in callsign for k in KEYWORDS):
        return False

    return any(callsign.endswith(s) for s in SUFFIXES)


def main():
    response = requests.get(VATSIM_DATA_URL, timeout=15)
    data = response.json()

    controllers = data.get("controllers", [])

    active_sectors = set()

    for c in controllers:
        callsign = c.get("callsign", "")
        if sector_matches(callsign):
            active_sectors.add(callsign)

    last_state = load_last_state()

    new_sectors = active_sectors - last_state

    if new_sectors:
        sector_list = "\n".join(f"• {s}" for s in sorted(new_sectors))

        message = (
            "<b>VATSIM Turkey sectors are now online.</b>\n\n"
            f"{sector_list}"
        )

        send_telegram(message)

    save_last_state(active_sectors)


if __name__ == "__main__":
    main()
