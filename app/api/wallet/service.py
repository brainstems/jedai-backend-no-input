import os
import boto3
from botocore.exceptions import ClientError

class WalletService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=os.environ.get("AWS_REGION"))
        self.wallets = self.dynamodb.Table('bs-olympics-whitelisted-addresses')
        

    def get_wallets(self):
        response = self.wallets.scan()
        wallets = response.get('Items', [])
        return wallets

    def get_wallet_by_address(self, address: str):
        try:
            response = self.wallets.get_item(Key={'address': address})
            wallet = response.get('Item')
            if not wallet:
                raise Exception("Wallet not found")
            return wallet
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])

        