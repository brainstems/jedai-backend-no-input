import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from typing import  Optional, Union

import boto3
import websockets
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from fastapi import WebSocket

from app.api.db.db import DatabaseOperations
from app.utils import generate_json_prompt

class PredictionService:
    def __init__(self) -> None:
        self.dynamodb = boto3.resource(
            "dynamodb", region_name=os.environ.get("AWS_REGION")
        )
        self.table = self.dynamodb.Table("bs-football-results")
        self.events = self.dynamodb.Table("bs-football-context-prompts")

    async def save_prediction(
        self, prediction: str, address: str
    ) -> Union[dict[str, str], str]:
        timestamp = datetime.now(timezone.utc).isoformat()
        prediction_id = str(uuid.uuid4())
        event = await self.get_daily_event()
        team = event["team"]
        try:
            response = self.table.query(
                IndexName="address-team-index",
                KeyConditionExpression=(
                    Key("address").eq(address) & Key("team").eq(team)
                ),
            )
            items = response.get("Items", [])
            if len(items) == 0:
                self.table.put_item(
                    Item={
                        "id": prediction_id,
                        "prediction": prediction,
                        "address": address,
                        "team": team,
                        "timestamp": timestamp,
                    }
                )
                return {
                    "prediction": prediction,
                    "address": address,
                    "timestamp": timestamp,
                }
            else:
                return f"Prediction already exists for this address: {address} and team: {team}"

        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise Exception("Prediction already exists")
            else:
                raise Exception(e.response["Error"]["Message"])

    @classmethod
    async def get_new_prediction(cls, prompt: str, client_websocket: WebSocket) -> None:
        event = await cls.get_daily_event()
        if not event:
            await client_websocket.send_text(
                json.dumps({"statusCode": 404, "body": "No daily event found"})
            )
            return

        system_context_prompt = event["contextPrompt"]
        assistant_context_prompt = event["assistantPrompt"]
        json_prompt = generate_json_prompt(
            prompt, system_context_prompt, assistant_context_prompt, max_tokens=10000
        )
        retry_counts = 0
        done = False
        while retry_counts < int(os.environ.get("RETRY_COUNT", "3")) and not done:
            try:
                async with websockets.connect(
                    f"ws://{os.environ.get('AKASH_ENDPOINT')}"
                ) as ws:
                    print("Connected to external websocket")
                    await ws.send(json_prompt)
                    print("Message sent to external websocket")
                    retry_counts = 0
                    while retry_counts < int(os.environ.get("RETRY_COUNT", "3")):
                        try:
                            tokens_count = 0
                            async for message in ws:
                                tokens_count += 1
                                print(
                                    "Received message from external websocket:", message
                                )
                                await client_websocket.send_text(
                                    json.dumps({"token": message})
                                )
                            print("TOKENS COUNT =", tokens_count)
                            if tokens_count > 0:
                                await client_websocket.send_text(
                                    json.dumps({"token": "END_OF_RESPONSE"})
                                )
                                done = True
                                break
                            else:
                                await asyncio.sleep(
                                    int(os.environ.get("RETRY_TIME", "30"))
                                )
                                print(
                                    "No messages received from external websocket. Retrying..."
                                )
                        except Exception as e:
                            print("Error receiving message via WebSocket:", e)
                            break
            except Exception as e:
                print(
                    f"Unable to connect to Inference Server. Retrying in {os.environ.get('RETRY_TIME')} seconds:",
                    e,
                )
                retry_counts += 1
                await asyncio.sleep(int(os.environ.get("RETRY_TIME", "30")))

    @classmethod
    async def get_daily_event(cls) -> Optional[dict[str, list | str]]:
        current_time = datetime.now()
        iso_date_str = current_time.isoformat()
        response = await DatabaseOperations.get_daily_event(iso_date_str)
        items = response.get("Items", [])
        if items:
            return items[0]
        else:
            return None

    @classmethod
    async def get_next_event(cls) -> Optional[dict[str, str]]:
        current_time = datetime.now()
        iso_date_str = current_time.isoformat()
        response = await DatabaseOperations.get_next_event(iso_date_str)
        items = response.get("Items", [])
        if items:
            next_event = min(items, key=lambda item: item["start_ts"])
            start_date = next_event["start_ts"]
            team = next_event["team"].replace("_", " VS ")
            return {"team": team, "start_date": start_date}
        else:
            return None

    async def available_to_predict(self, address: str) -> bool:
        event_of_the_day = await self.get_daily_event()
        if event_of_the_day is None:
            return False
        team = event_of_the_day["team"]
        try:
            response = await DatabaseOperations.available_to_predict(address, team)
            items = response.get("Items", [])
            return len(items) == 0
        except ClientError as e:
            raise Exception(e.response["Error"]["Message"])

    async def get_address_history(self, address: str) -> list[dict[str, str | int]]:
        try:
            response = self.table.query(
                IndexName="address-index",
                KeyConditionExpression=Key("address").eq(address),
            )
            items = response.get("Items", [])
            return items
        except ClientError as e:
            raise Exception(e.response["Error"]["Message"])
