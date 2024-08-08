import asyncio
import json
import os
import boto3
import websockets
from botocore.exceptions import ClientError
from datetime import date, datetime, timezone
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
        retry_counts = 0
        done = False
        while retry_counts < int(os.environ.get('RETRY_COUNT')) and not done:
            try:
                async with websockets.connect(f"ws://{os.environ.get('AKASH_ENDPOINT')}") as ws:
                    print('Connected to external websocket')
                    await ws.send(json_prompt)
                    print('Message sent to external websocket')
                    retry_counts = 0
                    while retry_counts < int(os.environ.get('RETRY_COUNT')):
                        try:
                            tokens_count = 0
                            async for message in ws:
                                tokens_count += 1
                                print('Received message from external websocket:', message)
                                await client_websocket.send_text(json.dumps({"token": message}))
                            print('TOKENS COUNT =', tokens_count)
                            if tokens_count > 0:
                                await client_websocket.send_text(json.dumps({"token": 'END_OF_RESPONSE'}))
                                done = True
                                break
                            else:
                                await asyncio.sleep(int(os.environ.get('RETRY_TIME'))) 
                                print('No messages received from external websocket. Retrying...')
                        except Exception as e:
                            print("Error receiving message via WebSocket:", e)
                            break
            except Exception as e:
                print(f"Unable to connect to Inference Server. Retrying in {os.environ.get('RETRY_TIME')} seconds:", e)
                retry_counts += 1
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
        
    def available_to_predict(self, address: str):
        today = date.today().isoformat()
        try:
            response = self.table.query(
                IndexName='address-timestamp-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('address').eq(address) & 
                                       boto3.dynamodb.conditions.Key('timestamp').begins_with(today)
            )
            items = response.get('Items', [])
            return len(items) == 0
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])