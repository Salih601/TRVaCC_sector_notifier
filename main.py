import requests
import time
import os

# Telegram ayarları (Render ENV'den gelir)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# VATSIM data
VATSIM_DATA_URL = "https://data.vatsim.net/v3/vatsim-data.json"

# Daha önce bildirilen pozisyonlar (spam önler)
seen_positions = set()

# Türkiye için izin verilen prefix ve suffix'ler
TR_PREFIXES = ("LT", "ANK", "IST", "IZM")
TR_SUFFIXES = ("_CTR", "_APP")

def send_telegram(message: str):
    """Telegram'a mesaj gönder"""
    if not BOT_TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload, timeout=10)

def check_vatsim():
    """VATSIM verisini kontrol et ve yeni TR APP/CTR'leri bildir"""
    response = requests.get(VATSIM_DATA_URL, timeout=20)
    data = response.json()

    for atc in data.get("controllers", []):
        callsign = atc.get("callsign", "")

        # Prefix + Suffix kontrolü
        if callsign.startswith(TR_PREFIXES) and callsign.endswith(TR_SUFFIXES):
            if callsign not in seen_positions:
                seen_positions.add(callsign)

                message = (
                    f"🇹🇷 {callsign} ONLINE\n"
                    f"👤 {atc.get('name', 'N/A')}\n"
                    f"📻 {atc.get('frequency', 'N/A')}"
                )
                send_telegram(message)

if __name__ == "__main__":
    send_telegram("✅ VATSIM TR APP/CTR notifier başlatıldı")

    while True:
        try:
            check_vatsim()
        except Exception as e:
            send_telegram(f"⚠️ Hata oluştu: {e}")
        time.sleep(60)
