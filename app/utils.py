import json
import boto3
import os
from datetime import datetime

def generate_json_prompt(prompt, system_context_prompt, assistant_context_prompt, max_tokens):
    json_dict = {
        'user_prompt': prompt,
        'system_context': system_context_prompt,
        'assistant_context': assistant_context_prompt,
        'max_tokens': max_tokens
    }
    json_prompt = json.dumps(json_dict)
    return json_prompt

async def send_token_to_client(token, websocket):
    try:
        await websocket.send_text(json.dumps({"token": token}))

    except Exception as e:
        print("Error sending token via WebSocket:", e)