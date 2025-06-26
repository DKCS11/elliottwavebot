import os
import base64
import requests
import tempfile
from flask import Flask, request
from dotenv import load_dotenv
from openai import OpenAI

# === Load environment variables ===
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
client = OpenAI(api_key=OPENAI_API_KEY)

# === Flask app ===
app = Flask(__name__)

# === GPT-4o reply generator ===
def generate_reply_gpt4o(message=None, image_path=None):
    try:
        if image_path:
            # Read image and encode in base64
            with open(image_path, "rb") as img:
                b64_image = base64.b64encode(img.read()).decode("utf-8")

            content = [
                {"type": "text", "text": message or "Please analyze this trading chart."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{b64_image}"
                    }
                }
            ]
        else:
            content = [{"type": "text", "text": message}]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an Elliott Wave trading assistant. Analyze charts and answer user trading questions with precision."
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=1000,
            temperature=0.5
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error processing chart: {str(e)}"

# === Telegram webhook ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": False, "error": "No chat ID"}

    if "photo" in message:
        photo = message["photo"][-1]
        file_id = photo["file_id"]

        # Get file path from Telegram
        file_info = requests.get(f"{TELEGRAM_API_URL}getFile?file_id={file_id}").json()
        file_path = file_info["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        # Download and save image
        img_response = requests.get(file_url)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(img_response.content)
            tmp_path = tmp_file.name

        # Generate AI reply from image
        reply = generate_reply_gpt4o(image_path=tmp_path)

        os.remove(tmp_path)

    elif "text" in message:
        user_text = message["text"]
        reply = generate_reply_gpt4o(message=user_text)

    else:
        reply = "❌ Unsupported message type. Please send a chart image or trading question."

    # Send reply to Telegram
    requests.post(TELEGRAM_API_URL + "sendMessage", json={
        "chat_id": chat_id,
        "text": reply
    })

    return {"ok": True}

# === Health check ===
@app.route("/")
def home():
    return "✅ GPT-4o Elliott Wave Bot is running!"

# === Run locally or via Render ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
