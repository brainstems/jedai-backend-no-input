from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.wallet.service import WalletService

router = APIRouter()


class Wallet(BaseModel):
    address: str


wallet_service = WalletService()


@router.post("/", response_model=Wallet)
def create_new_wallet(wallet: Wallet) -> Wallet:
    try:
        return wallet_service.create_wallet(wallet.address)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise HTTPException(status_code=400, detail="Wallet already exists")
        else:
            raise HTTPException(status_code=500, detail=e.response["Error"]["Message"])


@router.get("/", response_model=list[Wallet])
def get_wallets() -> list[Wallet]:
    try:
        return wallet_service.get_wallets()
    except ClientError as e:
        raise HTTPException(status_code=500, detail=e.response["Error"]["Message"])


@router.get("/{address}", response_model=Wallet)
def get_wallet_by_address(address: str) -> Wallet:
    try:
        return wallet_service.get_wallet_by_address(address)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
