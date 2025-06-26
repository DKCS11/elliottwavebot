import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
import tempfile

import openai

# === Load environment variables ===
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# === Generate reply using GPT-4o ===
def generate_reply_gpt4o(message=None, image_path=None):
    try:
        messages = [
            {"role": "system", "content": "You are an Elliott Wave chart analysis assistant. Analyze any uploaded trading chart and assist with wave structure, pattern identification, and trade ideas."}
        ]

        if message:
            messages.append({"role": "user", "content": message})

        files = None
        if image_path:
            with open(image_path, "rb") as image_file:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.5,
                    tools=[],
                    tool_choice=None,
                    images=[
                        {"image": image_file, "mime": "image/jpeg"}  # or image/png
                    ]
                )
            return response["choices"][0]["message"]["content"]

        # No image, just text
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
            temperature=0.5
        )
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Error processing chart: {str(e)}"

# === Telegram webhook ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")

    if "photo" in message:
        # Get highest quality photo
        photo = message["photo"][-1]
        file_id = photo["file_id"]

        # Get file path
        file_info = requests.get(f"{TELEGRAM_API_URL}getFile?file_id={file_id}").json()
        file_path = file_info["result"]["file_path"]

        # Download image
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        img_response = requests.get(file_url)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(img_response.content)
            tmp_path = tmp_file.name

        # Generate reply from image
        reply = generate_reply_gpt4o(image_path=tmp_path)

        os.remove(tmp_path)

    elif "text" in message:
        user_text = message["text"]
        reply = generate_reply_gpt4o(message=user_text)

    else:
        reply = "❌ Unsupported message type. Please send a chart or question."

    # Send reply
    requests.post(f"{TELEGRAM_API_URL}sendMessage", json={
        "chat_id": chat_id,
        "text": reply
    })

    return {"ok": True}

# === Health check ===
@app.route("/")
def home():
    return "✅ GPT-4o Chart Bot is running."

# === Run locally or in Render ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
