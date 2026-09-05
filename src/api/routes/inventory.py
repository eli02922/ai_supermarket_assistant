from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime, timedelta
from src.ml.inventory_analytics.stock_analyzer import StockAnalyzer
from src.ml.inventory_analytics.reorder_optimizer import ReorderOptimizer
from src.ml.inventory_analytics.trend_analyzer import TrendAnalyzer
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

stock_analyzer = StockAnalyzer()
reorder_optimizer = ReorderOptimizer()
trend_analyzer = TrendAnalyzer()


@router.get("/stockout-risk")
async def get_stockout_risk(
    days_ahead: int = Query(default=7, ge=1, le=30),
) -> List[Dict[str, Any]]:
    """Get products at risk of stockout"""
    try:
        return stock_analyzer.detect_stockouts(days_ahead=days_ahead)
    except Exception as e:
        logger.error(f"Error detecting stockout risk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/slow-moving")
async def get_slow_moving_products(
    days_lookback: int = Query(default=30, ge=7, le=90),
    threshold_sales: int = Query(default=10, ge=1),
) -> List[Dict[str, Any]]:
    """Get slow-moving products"""
    try:
        return stock_analyzer.identify_slow_moving_products(
            days_lookback=days_lookback,
            threshold_sales=threshold_sales,
        )
    except Exception as e:
        logger.error(f"Error getting slow-moving products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fast-moving")
async def get_fast_moving_products(
    days_lookback: int = Query(default=30, ge=7, le=90),
    threshold_percentile: float = Query(default=0.9, ge=0.5, le=0.99),
) -> List[Dict[str, Any]]:
    """Get fast-moving products"""
    try:
        return stock_analyzer.identify_fast_moving_products(
            days_lookback=days_lookback,
            threshold_percentile=threshold_percentile,
        )
    except Exception as e:
        logger.error(f"Error getting fast-moving products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reorder-suggestions")
async def get_reorder_suggestions() -> List[Dict[str, Any]]:
    """Get reorder suggestions"""
    try:
        return reorder_optimizer.get_reorder_suggestions()
    except Exception as e:
        logger.error(f"Error getting reorder suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/{product_id}")
async def get_product_trends(
    product_id: str,
    days_lookback: int = Query(default=90, ge=7, le=365),
) -> Dict[str, Any]:
    """Get product sales trends"""
    try:
        return trend_analyzer.analyze_product_trends(
            product_id=product_id,
            days_lookback=days_lookback,
        )
    except Exception as e:
        logger.error(f"Error getting product trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))