from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sklearn.model_selection import train_test_split
from src.db.session import get_db
from src.data.models.transaction import Transaction
from src.data.models.product import Product
from src.ml.demand_forecasting.feature_engineering import FeatureEngineer
from src.ml.demand_forecasting.models import DemandForecastingModel
from src.core.logging import get_logger
from src.core.config import settings

logger = get_logger(__name__)


class ModelTrainer:
    """Model training orchestration"""

    def __init__(self):
        self.feature_engineer = FeatureEngineer()

    def train(
        self,
        product_id: Optional[str] = None,
        store_id: Optional[str] = None,
        days_back: int = 365,
        model_type: str = "xgboost",
        test_size: float = 0.2,
    ) -> Dict[str, Any]:
        """Train a demand forecasting model"""
        logger.info(f"Training model for product {product_id}, store {store_id}")

        # Load data
        df = self._load_data(product_id, store_id, days_back)

        if df.empty:
            logger.warning("No data available for training")
            return {"status": "failed", "reason": "No data available"}

        # Prepare features
        X, y, feature_cols = self.feature_engineer.prepare_features(
            df, target_col="quantity", date_col="date"
        )

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        # Train model
        model = DemandForecastingModel(model_type=model_type)
        metrics = model.train(X_train, y_train, X_val, y_val)

        # Save model
        model_path = f"{settings.MODEL_REGISTRY_PATH}/{model_type}_{product_id or 'global'}_{store_id or 'all'}"
        model.save(model_path)

        return {
            "status": "success",
            "model_path": model_path,
            "metrics": metrics,
            "feature_cols": feature_cols,
            "n_samples": len(df),
            "n_features": len(feature_cols),
        }

    def _load_data(
        self,
        product_id: Optional[str] = None,
        store_id: Optional[str] = None,
        days_back: int = 365,
    ) -> pd.DataFrame:
        """Load transaction data for training"""
        db = next(get_db())

        try:
            query = db.query(Transaction)

            if product_id:
                query = query.filter(Transaction.product_id == product_id)
            if store_id:
                query = query.filter(Transaction.store_id == store_id)

            # Get data from last N days
            cutoff_date = datetime.now() - timedelta(days=days_back)
            query = query.filter(Transaction.date >= cutoff_date.date())

            # Aggregate by product, store, date
            df = pd.read_sql(query.statement, db.bind)

            if df.empty:
                return df

            # Aggregate daily sales
            df = df.groupby(
                ["product_id", "store_id", "date"]
            ).agg({"quantity": "sum", "total_amount": "sum"}).reset_index()

            logger.info(f"Loaded {len(df)} records from database")
            return df

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
        finally:
            db.close()