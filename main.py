import os
import json
import requests

VATSIM_URL = "https://data.vatsim.net/v3/vatsim-data.json"
STATE_FILE = "last_state.txt"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = os.getenv("CHAT_ID", "").split(",")


def send_telegram(message: str):
    for chat_id in CHAT_IDS:
        chat_id = chat_id.strip()
        if not chat_id:
            continue
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, json=payload, timeout=10)


def load_previous_state():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_state(sectors):
    with open(STATE_FILE, "w") as f:
        for s in sorted(sectors):
            f.write(s + "\n")


def get_current_sectors():
    response = requests.get(VATSIM_URL, timeout=15)
    data = response.json()

    sectors = set()

    for controller in data.get("controllers", []):
        callsign = controller.get("callsign", "")
        if "_" in callsign:
            sector = callsign.split("_")[0]
            if sector.startswith("LT"):
                sectors.add(sector)

    return sectors


def main():
    previous_sectors = load_previous_state()
    current_sectors = get_current_sectors()

    opened = current_sectors - previous_sectors
    closed = previous_sectors - current_sectors

    for sector in sorted(opened):
        send_telegram(
            f"<b>SEKTÖR AÇILDI</b>\n"
            f"✈️ {sector}"
        )

    for sector in sorted(closed):
        send_telegram(
            f"<b>SEKTÖR KAPANDI</b>\n"
            f"{sector}"
        )

    save_state(current_sectors)


if __name__ == "__main__":
    main()