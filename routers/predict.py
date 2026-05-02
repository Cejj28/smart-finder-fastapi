"""
routers/predict.py
------------------
ML prediction endpoint for lost/found item category classification.
"""

from fastapi import APIRouter, HTTPException
from schemas import CategoryInput, CategoryOutput

router = APIRouter()


@router.post(
    "/predict/category",
    response_model=CategoryOutput,
    summary="Predict item category",
    description=(
        "Given an item name and optional description, returns the predicted "
        "category (e.g. Electronics, Keys, Clothing) along with a confidence score."
    ),
    tags=["Machine Learning"],
)
def predict_category(data: CategoryInput):
    try:
        from ml_model import model_instance
        result = model_instance.predict(data.item_name, data.description or "")
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")