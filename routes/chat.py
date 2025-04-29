from flask import Blueprint, request, jsonify
import requests  # For calling an external DeepSeek API

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    if not user_msg:
        return jsonify({'reply': "I didn't catch that. Try again."})

    # Replace with real DeepSeek endpoint and key
    response = requests.post(
        "https://api.together.xyz/inference",
        headers={"Authorization": "Bearer sk-346e36f48a92463d85ebcf458103a400"},
        json={
            "model": "deepseek-chat",
            "prompt": user_msg,
            "max_tokens": 512,
            "temperature": 0.7
        }
    )

    reply = response.json().get("output", "Sorry, I couldn't respond.")
    return jsonify({'reply': reply})