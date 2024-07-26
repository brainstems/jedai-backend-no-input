from fastapi import WebSocket
from .utils import send_token_to_client

async def on_message(message, websocket: WebSocket):
    print(f"Received message: {message}")
    await send_token_to_client(message, websocket)

def on_error(error):
    print(f"Error occurred: {error}")
    return

def on_close():
    print("WebSocket connection closed")
    return

async def on_open(ws, final_prompt):
    print("WebSocket connection opened")
    await ws.send(final_prompt)
