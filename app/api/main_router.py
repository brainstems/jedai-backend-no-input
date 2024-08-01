from fastapi import APIRouter
from app.api.wallet.controller import router as wallet_router
from app.api.predictions.controller import router as predictions_router


api_router = APIRouter()

api_router.include_router(wallet_router, prefix="/wallet", tags=["wallet"])
api_router.include_router(predictions_router, prefix="/prediction", tags=["prediction"])

__all__ = ["api_router"]
