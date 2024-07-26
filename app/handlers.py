import json
import os
import websockets
from .websocket_handlers import on_message, on_error, on_close, on_open
from .utils import  generate_json_prompt
from .prompt_dynamo import get_prompts_from_dynamodb

first_non_empty_token_sent = False

async def handle_message(event, context, websocket):
    connection_id = event['requestContext']['connectionId']
    body = json.loads(event.get('body', '{}'))
    prompt = body.get('data', {}).get('prompt', '')
    if not prompt:
        await websocket.send_text(json.dumps({'statusCode': 400, 'body': 'No prompt provided'}))
        return
    

    # Get the prompt key from OpenAI // HARDCODED
    prompt_key = 'SALES'
    print("Prompt KEY from AI:", prompt_key)

    # Retrieve the system context prompt from DynamoDB using the prompt key
    prompts = get_prompts_from_dynamodb(prompt_key)
    system_context_prompt = prompts['contextPrompt']
    assistant_context_prompt = prompts['assistantPrompt']
    
    json_prompt = generate_json_prompt(prompt, system_context_prompt, assistant_context_prompt, max_tokens=10000)

    async with websockets.connect(f"ws://{os.environ.get('AKASH_ENDPOINT')}") as ws:
        await on_open(ws, json_prompt)

        try:
            async for message in ws:
                await on_message(message, websocket)
        except websockets.exceptions.ConnectionClosed as e:
            on_close()
        except Exception as e:
            on_error(str(e))
