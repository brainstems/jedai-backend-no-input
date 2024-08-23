from fastapi import APIRouter

from app.api.auth.controller import router as auth_router
from app.api.health import router as health_router
from app.api.predictions.controller import router as predictions_router
from app.api.wallet.controller import router as wallet_router

api_router = APIRouter()

api_router.include_router(wallet_router, prefix="/wallet", tags=["wallet"])
api_router.include_router(predictions_router, prefix="/prediction", tags=["prediction"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(health_router, prefix="/ping", tags=["health"])

__all__ = ["api_router"]
