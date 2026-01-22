import requests
import os

VATSIM_DATA_URL = "https://data.vatsim.net/v3/vatsim-data.json"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

STATE_FILE = "last_state.txt"

KEYWORDS = ["LR", "ANK"]
SUFFIXES = ["CTR", "APP", "TWR", "GND", "DEL"]


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

    active_sectors = {}
    last_state = load_last_state()

    for c in controllers:
        callsign = c.get("callsign", "")
        if sector_matches(callsign):
            active_sectors[callsign] = {
                "name": c.get("name", "Unknown"),
                "frequency": c.get("frequency", "N/A")
            }

    new_sectors = set(active_sectors.keys()) - last_state

    if new_sectors:
        lines = []
        for s in sorted(new_sectors):
            info = active_sectors[s]
            lines.append(
                f"▸ <b>{s}</b>\n"
                f"  │ {info['name']} — {info['frequency']}"
            )

        message = (
            "<b>VATSIM Turkey sectors are now online.</b>\n"
            "────────────────────────\n\n"
            + "\n\n".join(lines)
        )

        send_telegram(message)

    save_last_state(set(active_sectors.keys()))


if __name__ == "__main__":
    main()
