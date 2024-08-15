import asyncio
import json
import os
import boto3
import websockets
import uuid
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from datetime import date, datetime, timezone
from app.prompt_dynamo import get_prompts_from_dynamodb
from app.utils import generate_json_prompt

class PredictionService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=os.environ.get("AWS_REGION"))
        self.table = self.dynamodb.Table('bs-football-results')
        self.events = self.dynamodb.Table('bs-football-context-prompts')

    async def save_prediction(self, prediction: str, address: str):
        timestamp = datetime.now(timezone.utc).isoformat()
        prediction_id = str(uuid.uuid4())
        event = await self.get_daily_event()
        team = event['team']
        try:
            self.table.put_item(
                Item={
                    'id': prediction_id,
                    'prediction': prediction,
                    'address': address,
                    'team': team,
                    'timestamp': timestamp
                }
            )
            return {'prediction': prediction, 'address': address, 'timestamp': timestamp}
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise Exception("Prediction already exists")
            else:
                raise Exception(e.response['Error']['Message'])

    @classmethod
    async def get_new_prediction(cls, prompt: str, client_websocket):
        event = await cls.get_daily_event()
        if not event:
            await client_websocket.send_text(json.dumps({'statusCode': 404, 'body': 'No daily event found'}))
            return

        system_context_prompt = event['contextPrompt']
        assistant_context_prompt = event['assistantPrompt']
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
            
            # THIS SHOULD BE TE CODE, THE OTHER PART IS HARDCODED SO WE CAN GET AN EVENT
            # Get the current date and time
            # current_time = datetime.now()
            # current_timestamp = int(current_time.timestamp())  # Convert to UNIX timestamp
            
            # # Query the DynamoDB table with date range filter
            # response = cls().events.scan(
            #     FilterExpression=boto3.dynamodb.conditions.Attr('start_ts').lte(current_timestamp) &
            #                      boto3.dynamodb.conditions.Attr('end_ts').gte(current_timestamp)
            # )
            
            iso_date_str = '2024-08-17T20:30:00+0000'

            # Convert the ISO 8601 date string to a datetime object
            current_time = datetime.strptime(iso_date_str, '%Y-%m-%dT%H:%M:%S%z')

            # Convert the datetime object to a timestamp (if needed)
            current_timestamp = int(current_time.timestamp())

            # Convert back to ISO 8601 format if required for the query
            iso_date_str = current_time.isoformat()

            # Query the DynamoDB table with date range filter
            response = cls().events.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('start_ts').lte(iso_date_str) &
                                 boto3.dynamodb.conditions.Attr('end_ts').gte(iso_date_str)
            )
            
            items = response.get('Items', [])
            if items:
                # Return the first event from the result
                return items[0]
            else:
                return None
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])

    @classmethod
    async def get_next_event(cls):
        try:
            # Get the current date and time
            current_time = datetime.now()
            iso_date_str = current_time.isoformat()
            # Query the DynamoDB table for events that start after the current time
            response = cls().events.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('start_ts').gte(iso_date_str)
            )

            items = response.get('Items', [])

            if items:
                # Find the event with the earliest start_ts
                next_event = min(items, key=lambda item: item['start_ts'])
                start_date = next_event['start_ts']
                team = next_event['team'].replace('_', ' VS ')
                return {'team': team, 'start_date': start_date}
            else:
                return None
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])

    async def available_to_predict(self, address: str):
        event_of_the_day = await self.get_daily_event()
        team = event_of_the_day['team']
        try:
            response = self.table.query(
                IndexName='address-team-index',
                KeyConditionExpression=(
                    Key('address').eq(address) & Key('team').eq(team)
                )
            )
            items = response.get('Items', [])
            return len(items) == 0
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])
    
    async def get_address_history(self, address: str):
        try:
            response = self.table.query(
                IndexName='address-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('address').eq(address)
            )
            items = response.get('Items', [])
            return items
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])