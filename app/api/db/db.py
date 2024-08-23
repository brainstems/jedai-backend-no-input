import os
import uuid
from datetime import datetime, timezone

import boto3
from aiohttp import ClientError
from boto3.dynamodb.conditions import Key


class DatabaseOperations:
    def __init__(self):
        self.dynamodb = boto3.resource(
            "dynamodb", region_name=os.environ.get("AWS_REGION")
        )
        self.football_results = self.dynamodb.Table("bs-football-results")
        self.football_context_prompts = self.dynamodb.Table(
            "bs-football-context-prompts"
        )
        self.user_contacts = self.dynamodb.Table("bs-user-contacts")

    @classmethod
    def save_prediction(cls, address: str, prediction: str, team: str):
        """
        Saves a prediction to DynamoDB.

        Parameters:
        address (str): The address associated with the prediction.
        prediction (str): The prediction to be saved.
        team (str): The team associated with the prediction.

        Returns:
        dict: A dictionary containing the saved prediction, address, and timestamp if the prediction
        was saved successfully.
        str: A message indicating that a prediction already exists for the provided address and team.

        Exceptions:
        boto3.exceptions.Boto3Error: If there's an issue with querying or inserting data into DynamoDB.

        Notes:
        - The function first checks if a prediction for the given address and team already exists using the
        `address-team-index` index.
        - If no existing prediction is found, it generates a unique ID and saves the new prediction along
        with the timestamp.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        prediction_id = str(uuid.uuid4())
        try:
            response = cls().football_results.query(
                IndexName="address-team-index",
                KeyConditionExpression=(
                    Key("address").eq(address) & Key("team").eq(team)
                ),
            )
            items = response.get("Items", [])
            if len(items) == 0:
                cls().football_results.put_item(
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
    async def get_daily_event(cls, iso_date_str: str):
        """
        Retrieve the daily event from DynamoDB based on a specific date.

        Parameters:
        iso_date_str (str): The ISO 8601 formatted date string used to filter the event.

        Returns:
        dict: A dictionary containing the event data retrieved from the DynamoDB table.

        Raises:
        Exception: If there is an error querying DynamoDB, the specific error message is raised.

        Notes:
        - The function scans the `football_context_prompts` table to find an event that falls within the date range
        specified by `start_ts` and `end_ts`.
        - The date provided should be in UTC and formatted as an ISO 8601 string.
        """
        try:
            # Query the DynamoDB table with date range filter
            return cls().football_context_prompts.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr("start_ts").lte(
                    iso_date_str
                )
                & boto3.dynamodb.conditions.Attr("end_ts").gte(iso_date_str)
            )
        except ClientError as e:
            raise Exception(e.response["Error"]["Message"])

    @classmethod
    async def get_next_event(cls, iso_date_str: str):
        try:
            # Query the DynamoDB table for events that start after the current time
            return cls().football_context_prompts.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr("start_ts").gte(
                    iso_date_str
                )
            )
        except ClientError as e:
            raise Exception(e.response["Error"]["Message"])

    @classmethod
    async def available_to_predict(cls, address: str, team: str):
        try:
            return cls().football_results.query(
                IndexName="address-team-index",
                KeyConditionExpression=(
                    Key("address").eq(address) & Key("team").eq(team)
                ),
            )
        except ClientError as e:
            raise Exception(e.response["Error"]["Message"])
