import requests

HUGGINGFACE_API_TOKEN = "your_huggingface_api_key_here"
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

def generate_reply(message):
    headers = {"Authorization": f"Bearer {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}"}
    payload = {"inputs": message}

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result[0]['generated_text']
        else:
            return f"Error from Hugging Face: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"
