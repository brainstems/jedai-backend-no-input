import asyncio
import json
import os
import boto3
import websockets
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from app.prompt_dynamo import get_prompts_from_dynamodb
from app.utils import generate_json_prompt

class PredictionService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=os.environ.get("AWS_REGION"))
        self.table = self.dynamodb.Table('bs-olympics-results')
        self.events = self.dynamodb.Table('bs-olympics-context-prompts')

    def save_prediction(self, prediction: str, address: str):
        timestamp = datetime.now(timezone.utc).isoformat()
        try:
            self.table.put_item(
                Item={
                    'prediction': prediction,
                    'address': address,
                    'timestamp': timestamp
                },
                ConditionExpression='attribute_not_exists(prediction)'
            )
            return {'prediction': prediction, 'address': address, 'timestamp': timestamp}
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise Exception("Prediction already exists")
            else:
                raise Exception(e.response['Error']['Message'])

    @classmethod
    async def get_new_prediction(cls, prompt: str, client_websocket):
        prompt_key = 'MARATHON_SWIMMING_MEN'
        # prompt_key = await cls.get_daily_event()
        if not prompt_key:
            await client_websocket.send_text(json.dumps({'statusCode': 404, 'body': 'No daily event found'}))
            return
        prompts = get_prompts_from_dynamodb(prompt_key)
        system_context_prompt = prompts['contextPrompt']
        assistant_context_prompt = prompts['assistantPrompt']
        json_prompt = generate_json_prompt(prompt, system_context_prompt, assistant_context_prompt, max_tokens=10000)
       
        while True:
            try:
                async with websockets.connect(f"ws://{os.environ.get('AKASH_ENDPOINT')}") as ws:
                    print('Connected to external websocket')
                    await ws.send(json_prompt)
                    print('Message sent to external websocket')
                    try:
                        async for message in ws:
                            print('Received message from external websocket:', message)
                            await client_websocket.send_text(json.dumps({"token": message}))
                        await client_websocket.send_text(json.dumps({"token": 'END_OF_RESPONSE'}))
                    except Exception as e:
                        print("Error receiving message via WebSocket:", e)
                    break
            except Exception as e:
                print(f"Unable to connect to Inference Server. Retrying in {os.environ.get('RETRY_TIME')} seconds:", e)
                await asyncio.sleep(int(os.environ.get('RETRY_TIME'))) 

    @classmethod
    async def get_daily_event(cls):
        try:
            current_day = datetime.now().strftime('%A').upper()
            response = cls().events.query(
                IndexName='day-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('day').eq(current_day)
            )
            items = response.get('Items', [])
            if items:
                daily_event = items[0].get('sport_key', '')
                return daily_event
            else:
                return None
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])