from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from src.ml.demand_forecasting.predictor import DemandPredictor
from src.ml.demand_forecasting.trainer import ModelTrainer
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

predictor = DemandPredictor()
trainer = ModelTrainer()


class ForecastRequest(BaseModel):
    product_id: str
    store_id: Optional[str] = None
    horizon_days: int = 30


class ForecastResponse(BaseModel):
    product_id: str
    product_name: str
    store_id: Optional[str] = None
    store_name: Optional[str] = None
    forecast: List[Dict[str, Any]]
    summary: Dict[str, Any]


class TrainRequest(BaseModel):
    product_id: Optional[str] = None
    store_id: Optional[str] = None
    days_back: int = 365
    model_type: str = "xgboost"


@router.post("/predict", response_model=ForecastResponse)
async def predict_demand(request: ForecastRequest) -> ForecastResponse:
    """Predict demand for a product"""
    try:
        forecast = predictor.predict(
            product_id=request.product_id,
            store_id=request.store_id,
            horizon_days=request.horizon_days,
        )
        return ForecastResponse(**forecast)
    except Exception as e:
        logger.error(f"Demand prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def train_model(request: TrainRequest) -> Dict[str, Any]:
    """Train a demand forecasting model"""
    try:
        result = trainer.train(
            product_id=request.product_id,
            store_id=request.store_id,
            days_back=request.days_back,
            model_type=request.model_type,
        )
        return result
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}")
async def get_product_forecast(
    product_id: str,
    horizon_days: int = Query(default=7, ge=1, le=90),
) -> Dict[str, Any]:
    """Get forecast for a specific product"""
    try:
        forecast = predictor.predict(
            product_id=product_id,
            horizon_days=horizon_days,
        )
        return forecast
    except Exception as e:
        logger.error(f"Error getting product forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stockout-risk")
async def get_stockout_risk(
    days_ahead: int = Query(default=7, ge=1, le=30),
) -> List[Dict[str, Any]]:
    """Get products at risk of stockout"""
    try:
        return predictor.detect_stockout_risk(days_ahead=days_ahead)
    except Exception as e:
        logger.error(f"Error detecting stockout risk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reorder-suggestions")
async def get_reorder_suggestions() -> List[Dict[str, Any]]:
    """Get reorder suggestions"""
    try:
        return predictor.get_reorder_suggestions()
    except Exception as e:
        logger.error(f"Error getting reorder suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))