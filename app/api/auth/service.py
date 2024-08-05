import os
from app.api.wallet.service import WalletService
import jwt
from datetime import datetime, timedelta, timezone
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

class AuthService:
    @staticmethod
    def generate_token(wallet_address):
        expiration = datetime.now(timezone.utc) + timedelta(minutes=int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 10080)))
        payload = {
            'wallet_address': wallet_address,
            'exp': expiration
        }
        token = jwt.encode(payload, os.environ.get('SECRET_KEY'), algorithm="HS256")
        return token

    @staticmethod
    async def authenticate(address):
        wallet_service = WalletService()
        wallet = wallet_service.get_wallet_by_address(address)
        if not wallet:
            return None
        token = AuthService.generate_token(address)
        return token

    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            return payload
        except ExpiredSignatureError:
            raise ValueError("Token has expired")
        except InvalidTokenError:
            raise ValueError("Invalid token")
