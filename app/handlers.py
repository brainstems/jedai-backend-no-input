import json
import os

from app.api.auth.service import AuthService
from app.api.predictions.service import PredictionService


async def handle_message(event, client_websocket):
    body = json.loads(event.get('body', '{}'))
    data = body.get('data', {})
    prompt = data.get('prompt', '')
    address = data.get('address', '')
    api_key = data.get('api_key_auth', '')
    if not api_key :
        await client_websocket.send_text(json.dumps({'statusCode': 400, 'body': 'No api key provided'}))
        return

    if api_key != os.environ.get('API_KEY_AUTH'):
        await client_websocket.send_text(json.dumps({'statusCode': 401, 'body': 'Unauthorized'}))
        return

    if not prompt:
        await client_websocket.send_text(json.dumps({'statusCode': 400, 'body': 'No prompt provided'}))
        return

    token = data.get('token', '')
    if not token:
        await client_websocket.send_text(json.dumps({'statusCode': 400, 'body': 'No token provided'}))
        return

    try:
        AuthService.verify_token(token)
    except ValueError as e:
        error_message = str(e)
        await client_websocket.send_text(json.dumps({'statusCode': 498, 'body': error_message}))
        return

    await PredictionService.get_new_prediction(prompt, client_websocket, address)
    print('Finished getting new prediction')


