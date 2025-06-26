import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

# === Flask app ===
app = Flask(__name__)

# === Config from .env ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# === Safety checks ===
if not OPENROUTER_API_KEY or not BOT_TOKEN:
    raise RuntimeError("❌ Missing OPENROUTER_API_KEY or BOT_TOKEN in .env file.")

# === AI reply logic ===
def generate_reply(message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-4-maverick:free",
        "messages": [
            {"role": "system", "content": "You are a highly skilled Elliott Wave trading assistant who manages trades and evolves with new strategies."},
            {"role": "user", "content": message}
        ]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as errh:
        return f"❌ HTTP Error: {errh}\n{response.text}"
    except requests.exceptions.RequestException as err:
        return f"❌ Request Error: {err}"
    except Exception as e:
        return f"❌ Unexpected Error: {e}"

# === Telegram webhook ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    text = data.get("message", {}).get("text", "")

    if chat_id and text:
        reply = generate_reply(text)
        requests.post(TELEGRAM_API_URL + "sendMessage", json={
            "chat_id": chat_id,
            "text": reply
        })

    return {"ok": True}

# === Health check ===
@app.route("/")
def home():
    return "✅ Elliott Wave Trading Bot is online."

# === Run on Render ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
