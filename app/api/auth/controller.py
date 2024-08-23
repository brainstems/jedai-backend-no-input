from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.auth.service import AuthService

router = APIRouter()


class AuthRequest(BaseModel):
    address: str


@router.post("/")
async def authenticate(auth_request: AuthRequest):
    token = AuthService.authenticate(auth_request.address)
    if token is None:
        raise HTTPException(
            status_code=401, detail="Wallet not found or authentication failed"
        )
    return {"token": token}


@router.post("/verify")
async def verify_token(token: str):
    try:
        payload = AuthService.verify_token(token)
        return {"valid": True, "payload": payload}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
