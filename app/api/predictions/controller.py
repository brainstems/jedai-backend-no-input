from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .service import PredictionService

router = APIRouter()

prediction_service = PredictionService()

class PredictionRequest(BaseModel):
    prediction: str
    address: str

@router.post("/", response_model=dict)
async def create_prediction(request: PredictionRequest):
    prediction_service = PredictionService()
    try:
        result = prediction_service.save_prediction(request.prediction, request.address)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/new", response_model=dict)
async def get_new_prediction():
    PredictionService.get_new_prediction()