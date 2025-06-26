import os
import requests
from flask import Flask, request

app = Flask(__name__)

# === Configuration ===
BOT_TOKEN = "7960553174:AAE2UcsTyALD69ThMM_Bi2Vuxs9Z1GvLsLc"
HUGGINGFACE_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-alpha"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# === Hugging Face AI Response ===
def generate_reply(message):
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": f"You are a skilled Elliott Wave trading assistant. Respond concisely and clearly to: {message}",
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result[0]['generated_text']
        else:
            return f"❌ Hugging Face Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"⚠️ Exception occurred: {e}"

# === Telegram Webhook Handler ===
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

# === Default Route ===
@app.route("/")
def home():
    return "Your Elliott Wave AI Bot is live and ready to trade!"

# === Server Start ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

