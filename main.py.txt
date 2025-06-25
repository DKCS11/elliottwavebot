import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "7960553174:AAE2UcsTyALD69ThMM_Bi2Vuxs9Z1GvLsLc"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

def generate_reply(message):
    msg = message.lower()
    if "wave" in msg:
        return "Impulse = 5 waves, Correction = 3 waves. We might be in Wave 5."
    elif "tp" in msg:
        return "TP1: 6090, TP2: 6020, TP3: 5950"
    elif "macd" in msg:
        return "MACD divergence usually means Wave 5 is near the end."
    elif "help" in msg:
        return "Commands: wave, tp, macd, help"
    else:
        return "Trade smart. Confirm structure before execution."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        message_text = data["message"].get("text", "")
        reply = generate_reply(message_text)
        requests.post(TELEGRAM_API_URL + "sendMessage", json={
            "chat_id": chat_id,
            "text": reply
        })
    return {"ok": True}

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
