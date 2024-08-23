import json
import os

from fastapi import HTTPException


def generate_json_prompt(
    prompt, system_context_prompt, assistant_context_prompt, max_tokens
):
    json_dict = {
        "user_prompt": prompt,
        "system_context": system_context_prompt,
        "assistant_context": assistant_context_prompt,
        "max_tokens": max_tokens,
    }
    json_prompt = json.dumps(json_dict)
    return json_prompt


async def send_token_to_client(token, websocket):
    try:
        await websocket.send_text(json.dumps({"token": token}))

    except Exception as e:
        print("Error sending token via WebSocket:", e)


def check_api_key(api_key: str):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is missing")
    if api_key != os.environ.get("API_KEY_AUTH"):
        raise HTTPException(status_code=403, detail="Invalid API key")
