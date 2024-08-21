
from datetime import datetime, timezone
import os
import uuid
from aiohttp import ClientError
from boto3.dynamodb.conditions import Key
import boto3

class DatabaseOperations:
    def __init__(self):
            self.dynamodb = boto3.resource('dynamodb', region_name=os.environ.get("AWS_REGION"))
            self.football_results = self.dynamodb.Table('bs-football-results')
            self.football_context_prompts = self.dynamodb.Table('bs-football-context-prompts')
            self.user_contacts = self.dynamodb.Table('bs-user-contacts')

    @classmethod
    def save_prediction(cls, address: str, prediction: str, team: str):
        """
        Save prediction to DynamoDB
        """
        if os.environ.get('ENVIRONMENT') == 'QA':
            return { 'prediction': prediction, 'address': address, 'timestamp': timestamp}
        timestamp = datetime.now(timezone.utc).isoformat()
        prediction_id = str(uuid.uuid4())
        try:
            response = cls().football_results.query(
                IndexName='address-team-index',
                KeyConditionExpression=(
                    Key('address').eq(address) & Key('team').eq(team)
                )
            )
            items = response.get('Items', [])
            if len(items) == 0: 
                cls().football_results.put_item(
                    Item={
                        'id': prediction_id,
                        'prediction': prediction,
                        'address': address,
                        'team': team,
                        'timestamp': timestamp
                    }
                )
                return {'prediction': prediction, 'address': address, 'timestamp': timestamp}
            else:
                return f"Prediction already exists for this address: {address} and team: {team}"
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise Exception("Prediction already exists")
            else:
                raise Exception(e.response['Error']['Message'])

    @classmethod
    async def get_daily_event(cls, iso_date_str: str):
        """
        Get daily event from DynamoDB
        """
    
        try:
            # Query the DynamoDB table with date range filter
            return cls().football_context_prompts.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('start_ts').lte(iso_date_str) &
                                    boto3.dynamodb.conditions.Attr('end_ts').gte(iso_date_str)
            )
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])
        
    @classmethod
    def get_next_event(cls, iso_date_str: str):
        try:
            # Query the DynamoDB table for events that start after the current time
            return cls().football_context_prompts.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('start_ts').gte(iso_date_str)
            )
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])

    @classmethod
    async def available_to_predict(cls, address: str, team: str):
        try:
            return cls().football_results.query(
                IndexName='address-team-index',
                KeyConditionExpression=(
                    Key('address').eq(address) & Key('team').eq(team)
                )
            )
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])