import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

# === Flask app setup ===
app = Flask(__name__)

# === Configuration ===
BOT_TOKEN = "7960553174:AAE2UcsTyALD69ThMM_Bi2Vuxs9Z1GvLsLc"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# === Safety check ===
if not OPENROUTER_API_KEY:
    raise RuntimeError("❌ OPENROUTER_API_KEY is not set in environment variables!")

# === AI reply logic ===
def generate_reply(message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openrouter/openai/gpt-3.5-turbo",  # ✅ Corrected model name
        "messages": [
            {"role": "system", "content": "You are an Elliott Wave trading assistant."},
            {"role": "user", "content": message}
        ]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15)
        print(f"🔁 OpenRouter response: {response.status_code} - {response.text}")  # For debugging
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as errh:
        return f"❌ HTTP Error: {errh}\n{response.text}"
    except requests.exceptions.RequestException as err:
        return f"❌ Request Error: {err}"
    except Exception as e:
        return f"❌ Unexpected Error: {e}"

# === Telegram webhook endpoint ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    chat = data.get("message", {}).get("chat", {})
    text = data.get("message", {}).get("text", "")

    if chat and text:
        reply = generate_reply(text)
        requests.post(TELEGRAM_API_URL + "sendMessage", json={
            "chat_id": chat["id"],
            "text": reply
        })

    return {"ok": True}

# === Health check route ===
@app.route("/")
def home():
    return "✅ Elliott Wave Bot via OpenRouter is running!"

# === Run the app locally ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
