import json
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from app.api.wallet.service import WalletService  
import websockets

from app.prompt_dynamo import get_prompts_from_dynamodb
from app.utils import generate_json_prompt

class PredictionService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=os.environ.get("AWS_REGION"))
        self.table = self.dynamodb.Table('bs-olympics-results')

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
    async def handle_socket_message(cls, event, websocket):
        print("Handling socket message")
        body = json.loads(event.get('body', '{}'))
        data = body.get('data', {})
        prompt = data.get('prompt', '')
        address = data.get('address', '')
        if not address:
            await websocket.send_text(json.dumps({'statusCode': 400, 'body': 'No address provided'}))
            return
        else:
            wallet_service = WalletService()
            wallet = wallet_service.get_wallet_by_address(address)
            if not wallet:
                await websocket.send_text(json.dumps({'statusCode': 400, 'body': 'Wallet not found'}))
                return
        print("Calling get_new_prediction")
        await cls.get_new_prediction(websocket, address, prompt)
    
    @classmethod
    async def get_new_prediction(cls, client_websocket, address: str, prompt: str):
        prompt_key = 'MARATHON_SWIMMING_MEN'
        prompts = get_prompts_from_dynamodb(prompt_key)
        system_context_prompt = prompts['contextPrompt']
        assistant_context_prompt = prompts['assistantPrompt']
        
        json_prompt = generate_json_prompt(prompt, system_context_prompt, assistant_context_prompt, max_tokens=10000)
        json_prompt2 = json.dumps({
            "user_prompt": "Give me a new prediction for this event",
            "system_context": ("You are an olympics winner predictor for Men's 10K marathon swimming sport. "
                               "You will be asked to predict who is going to win the gold medal and their timing.\n"
                               "As context, I'll give you the historical data of athletes, birth dates and the result "
                               "of the latest championships.\nReturn only the predicted winner and the predicted timing "
                               "with no other information."),
            "assistant_context": ("List of athletes and their date of birth:\nCountry,Name,Date of Birth\n"
                                 "Australia,Lee Kyle,23 Feb 2002\nAustralia,Sloman Nick,30 Oct 1997\n"
                                 "Austria,Auboeck Felix,19 Dec 1996\nAustria,Hercog Jan,10 Feb 1998\n"
                                 "Brazil,Costa Guilherme,1 Oct 1998\nCzechia,Straka Martin,12 Nov 2000\n"
                                 "Ecuador,Farinango Berru David Andres,20 Oct 2000\nFrance,Fontaine Logan,25 Mar 1999\n"
                                 "France,Olivier Marc-Antoine,18 Jun 1996\n"),
            "max_tokens": 10000
        })
        
        print("Connecting to external websocket")
        async with websockets.connect(f"ws://{os.environ.get('AKASH_ENDPOINT')}") as ws:
            print('Connected to external websocket')
            await ws.send(json_prompt2)
            print('Message sent to external websocket')
            try:
                async for message in ws:
                    print('Received message from external websocket:', message)
                    await client_websocket.send_text(json.dumps({"token": message}))
            except Exception as e:
                print("Error receiving message via WebSocket:", e)
        print('Finished getting new prediction')
        