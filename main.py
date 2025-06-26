import os
import requests
from flask import Flask, request

app = Flask(__name__)

# === CONFIGURATION ===
BOT_TOKEN = "7960553174:AAE2UcsTyALD69ThMM_Bi2Vuxs9Z1GvLsLc"  # <-- Your Telegram Bot Token
HUGGINGFACE_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

# === TELEGRAM API ===
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# === HANDLE INCOMING MESSAGES ===
def generate_reply(message):
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": f"You are a helpful and skilled Elliott Wave trading assistant. Answer the following: {message}",
        "parameters": {"max_new_tokens": 200}
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result[0]["generated_text"]
        else:
            return f"❌ HuggingFace Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"⚠️ Error: {e}"

# === TELEGRAM WEBHOOK ROUTE ===
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

# === ROOT ENDPOINT ===
@app.route("/")
def home():
    return "Elliott Wave Bot is running with Hugging Face AI!"

# === START SERVER ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

