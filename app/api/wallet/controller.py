from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.utils import BaseController
from app.api.wallet.service import WalletService

router = APIRouter()


class Wallet(BaseModel):
    address: str


class WalletController(BaseController):
    def __init__(self):
        self.wallet_service = WalletService()


wallet_controller = WalletController()


@router.post("/", response_model=Wallet)
def create_new_wallet(wallet: Wallet) -> Wallet:
    try:
        return wallet_controller.wallet_service.create_wallet(wallet.address)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Wallet already exists"
            )
        else:
            wallet_controller.handle_backend_error(e)


@router.get("/", response_model=list[Wallet])
def get_wallets() -> list[Wallet]:
    try:
        wallets = wallet_controller.wallet_service.get_wallets()
        if not wallets:
            wallet_controller.handle_no_event("No wallets found")
        return wallets
    except ClientError as e:
        wallet_controller.handle_backend_error(e)


@router.get("/{address}", response_model=Wallet)
def get_wallet_by_address(address: str) -> Wallet:
    try:
        wallet = wallet_controller.wallet_service.get_wallet_by_address(address)
        if not wallet:
            wallet_controller.handle_no_event("Wallet not found")
        return wallet
    except Exception as e:
        wallet_controller.handle_backend_error(e)
