from fastapi import APIRouter
from schemas import InputData, OutputData
from ml_model import model_instance

router = APIRouter()

@router.post("/predict", response_model=OutputData) # [cite: 84]
def predict(data: InputData):
    return model_instance.predict(data.text) # [cite: 85]