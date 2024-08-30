from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.auth.service import AuthService
from app.api.utils import BaseController

router = APIRouter()


class AuthRequest(BaseModel):
    address: str


class AuthController(BaseController):
    @staticmethod
    async def authenticate(auth_request: AuthRequest) -> dict[str, str]:
        try:
            token = AuthService.authenticate(auth_request.address)
            if token is None:
                raise HTTPException(
                    status_code=401, detail="Wallet not found or authentication failed"
                )
            return {"token": token}
        except Exception as e:
            AuthController.handle_backend_error(e)

    @staticmethod
    async def verify_token(token: str) -> dict[str, Any]:
        try:
            payload = AuthService.verify_token(token)
            return {"valid": True, "payload": payload}
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            AuthController.handle_backend_error(e)


@router.post("/", response_model=dict[str, str])
async def authenticate(auth_request: AuthRequest) -> dict[str, str]:
    return await AuthController.authenticate(auth_request)


@router.post("/verify", response_model=dict[str, dict | bool])
async def verify_token(token: str) -> dict[str, Any]:
    return await AuthController.verify_token(token)
