from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from app.utils import check_api_key
from .service import PredictionService

router = APIRouter()

prediction_service = PredictionService()

class PredictionRequest(BaseModel):
    prediction: str
    address: str

async def get_api_key(request: Request):
    api_key = request.headers.get("api_key_auth")
    check_api_key(api_key)
    return api_key

@router.post("/", response_model=dict)
async def create_prediction(request: PredictionRequest, 
                            # api_key: str = Depends(get_api_key)
                            ):
    try:
        result = await prediction_service.save_prediction(request.prediction, request.address)
        if isinstance(result, dict):
            return {"result": result}
        else:
            return {"error": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/new", response_model=dict)
async def get_new_prediction(api_key: str = Depends(get_api_key)):
    try:
        result = await  prediction_service.get_new_prediction()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily", response_model=dict)
async def get_daily_event(
    # api_key: str = Depends(get_api_key)
                          ):
    try:
        
        result = await prediction_service.get_daily_event()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available", response_model=dict)
async def available_to_predict(address: str, 
                            #   api_key: str = Depends(get_api_key)
                              ):
    try:
        available = await prediction_service.available_to_predict(address)
        return {"available": available}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=dict)
async def get_address_history(address: str):
    try:
        history = await prediction_service.get_address_history(address)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/next", response_model=dict)
async def get_next_event(
    # api_key: str = Depends(get_api_key)
                          ):
    try:
        result = await prediction_service.get_next_event()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))