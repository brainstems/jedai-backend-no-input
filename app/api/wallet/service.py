import os
import boto3
from botocore.exceptions import ClientError

class WalletService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=os.environ.get("AWS_REGION"))
        self.wallets = self.dynamodb.Table('bs-user-contacts')


    def get_wallets(self):
        response = self.wallets.scan()
        wallets = response.get('Items', [])
        return wallets

    def get_wallet_by_address(self, address: str):
        try:
            response = self.wallets.query(
                IndexName='address-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('address').eq(address)
            )
            items = response.get('Items')
            if not items:
                raise Exception("Wallet not found")
            return items[0] 
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])

        