from fastapi import WebSocket

from .utils import send_token_to_client


async def on_message(message: str, websocket: WebSocket) -> None:
    print(f"Received message: {message}")
    await send_token_to_client(message, websocket)


def on_error(error: Exception) -> None:
    print(f"Error occurred: {error}")
    return


def on_close() -> None:
    print("WebSocket connection closed")
    return


async def on_open(ws: WebSocket, final_prompt: str) -> None:
    print("WebSocket connection opened")
    await ws.send(final_prompt)
