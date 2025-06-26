import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

# === Load environment variables from .env or Render ===
load_dotenv()

# === Flask app ===
app = Flask(__name__)

# === Config ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN is not set in environment variables!")
if not OPENROUTER_API_KEY:
    raise RuntimeError("❌ OPENROUTER_API_KEY is not set in environment variables!")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# === AI reply logic ===
def generate_reply(message: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openrouter/openai/gpt-4",  # Using GPT-4 model here
        "messages": [
            {"role": "system", "content": "You are an Elliott Wave trading assistant and trade manager."},
            {"role": "user", "content": message}
        ]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as errh:
        return f"❌ HTTP Error: {errh} - {response.text}"
    except requests.exceptions.RequestException as err:
        return f"❌ Request Error: {err}"
    except Exception as e:
        return f"❌ Unexpected Error: {e}"

# === Telegram webhook endpoint ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json(force=True)
    chat = data.get("message", {}).get("chat", {})
    text = data.get("message", {}).get("text", "")

    if chat and text:
        reply = generate_reply(text)
        requests.post(TELEGRAM_API_URL + "sendMessage", json={
            "chat_id": chat.get("id"),
            "text": reply
        })

    return {"ok": True}

# === Health check route ===
@app.route("/")
def home():
    return "✅ Elliott Wave Trade Manager Bot via OpenRouter is running!"

# === Run app on Render ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
