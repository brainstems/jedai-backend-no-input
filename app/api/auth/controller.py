from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.auth.service import AuthService

router = APIRouter()


class AuthRequest(BaseModel):
    address: str


@router.post("/", response_model=dict[str, str])
async def authenticate(auth_request: AuthRequest) -> dict[str, str]:
    token = AuthService.authenticate(auth_request.address)
    if token is None:
        raise HTTPException(
            status_code=401, detail="Wallet not found or authentication failed"
        )
    return {"token": token}


@router.post("/verify", response_model=dict[str, dict | bool])
async def verify_token(token: str) -> dict[str, Any]:
    try:
        payload = AuthService.verify_token(token)
        return {"valid": True, "payload": payload}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
