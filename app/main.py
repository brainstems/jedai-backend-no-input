import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.main_router import api_router
from app.handlers import handle_message

load_dotenv()

app = FastAPI()
clients: set[WebSocket] = set()

origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    try:
        while True:
            data: str = await websocket.receive_text()
            event = {
                "body": data,
                "requestContext": {"connectionId": websocket.client.host},
            }
            asyncio.create_task(handle_message(event, websocket))
    except WebSocketDisconnect:
        print("Client disconnected")
        clients.remove(websocket)
