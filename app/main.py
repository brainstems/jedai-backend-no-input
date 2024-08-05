import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from dotenv import load_dotenv
from app.api.main_router import api_router
from app.handlers import handle_message
load_dotenv()

app = FastAPI()
clients = set()

app.include_router(api_router, prefix="/api")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            event = {'body': data, 'requestContext': {'connectionId': websocket.client.host}}
            asyncio.create_task(handle_message(event, websocket))
    except WebSocketDisconnect:
        print("Client disconnected")
        clients.remove(websocket)
    finally:
        await websocket.close()
