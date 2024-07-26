from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .handlers import handle_message
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            event = {'body': data, 'requestContext': {'connectionId': websocket.client.host}}
            await handle_message(event, None, websocket)
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        await websocket.close()

