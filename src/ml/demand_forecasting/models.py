import pickle
import json
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
from prophet import Prophet
import mlflow
import mlflow.sklearn
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import ModelTrainingError, ModelNotFoundError

logger = get_logger(__name__)


class DemandForecastingModel:
    """Demand forecasting model wrapper"""

    def __init__(self, model_type: str = "xgboost"):
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.feature_importance = None
        self.metrics = {}
        self.model_path = f"{settings.MODEL_REGISTRY_PATH}/{model_type}"

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, float]:
        """Train the model"""
        logger.info(f"Training {self.model_type} model...")

        with mlflow.start_run(run_name=f"{self.model_type}_training"):
            # Log parameters
            mlflow.log_params(params or {})

            # Create model based on type
            if self.model_type == "xgboost":
                self.model = xgb.XGBRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42,
                    **(params or {}),
                )
            elif self.model_type == "random_forest":
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    **(params or {}),
                )
            elif self.model_type == "gradient_boosting":
                self.model = GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42,
                    **(params or {}),
                )
            elif self.model_type == "linear":
                self.model = LinearRegression()
            elif self.model_type == "prophet":
                return self._train_prophet(X_train, y_train)
            else:
                raise ValueError(f"Unknown model type: {self.model_type}")

            # Train model
            self.model.fit(X_train, y_train)

            # Calculate metrics
            y_pred = self.model.predict(X_train)
            metrics = {
                "train_mae": mean_absolute_error(y_train, y_pred),
                "train_rmse": np.sqrt(mean_squared_error(y_train, y_pred)),
                "train_r2": r2_score(y_train, y_pred),
            }

            if X_val is not None and y_val is not None:
                y_pred_val = self.model.predict(X_val)
                metrics.update({
                    "val_mae": mean_absolute_error(y_val, y_pred_val),
                    "val_rmse": np.sqrt(mean_squared_error(y_val, y_pred_val)),
                    "val_r2": r2_score(y_val, y_pred_val),
                })

            # Store metrics
            self.metrics = metrics

            # Log metrics
            for key, value in metrics.items():
                mlflow.log_metric(key, value)

            # Log feature importance
            if hasattr(self.model, "feature_importances_"):
                self.feature_importance = dict(
                    zip(X_train.columns, self.model.feature_importances_)
                )
                # Log feature importance as artifact
                importance_df = pd.DataFrame(
                    list(self.feature_importance.items()),
                    columns=["feature", "importance"]
                )
                importance_df.to_csv("feature_importance.csv", index=False)
                mlflow.log_artifact("feature_importance.csv")

            # Save model
            mlflow.sklearn.log_model(self.model, self.model_type)

            logger.info(f"Training completed. Metrics: {metrics}")
            return metrics

    def _train_prophet(
        self, X_train: pd.DataFrame, y_train: pd.Series
    ) -> Dict[str, float]:
        """Train Prophet model"""
        # Prepare data for Prophet
        df_prophet = pd.DataFrame({
            "ds": X_train.index if hasattr(X_train, "index") else range(len(X_train)),
            "y": y_train.values,
        })

        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
        )

        # Add additional regressors if available
        if hasattr(X_train, "columns"):
            for col in X_train.columns:
                if col not in ["ds", "y"]:
                    model.add_regressor(col)

        model.fit(df_prophet)
        self.model = model

        # Calculate metrics
        future = model.make_future_dataframe(periods=0)
        forecast = model.predict(future)
        y_pred = forecast["yhat"]

        metrics = {
            "train_mae": mean_absolute_error(y_train, y_pred),
            "train_rmse": np.sqrt(mean_squared_error(y_train, y_pred)),
            "train_r2": r2_score(y_train, y_pred),
        }

        self.metrics = metrics
        logger.info(f"Prophet training completed. Metrics: {metrics}")
        return metrics

    def predict(
        self,
        X: pd.DataFrame,
        future_days: int = 30,
    ) -> np.ndarray:
        """Make predictions"""
        if self.model is None:
            raise ModelNotFoundError("Model not trained or loaded")

        try:
            if self.model_type == "prophet":
                return self._predict_prophet(X, future_days)
            else:
                return self.model.predict(X)
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise

    def _predict_prophet(
        self, X: pd.DataFrame, future_days: int = 30
    ) -> np.ndarray:
        """Make predictions with Prophet"""
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=future_days)

        # Add regressors
        if hasattr(X, "columns"):
            for col in X.columns:
                if col in future.columns:
                    future[col] = X[col].values[0] if len(X) > 0 else 0

        forecast = self.model.predict(future)
        return forecast["yhat"].values[-future_days:]

    def save(self, path: Optional[str] = None) -> None:
        """Save model to disk"""
        if self.model is None:
            raise ModelNotFoundError("Cannot save untrained model")

        path = path or self.model_path
        with open(f"{path}.pkl", "wb") as f:
            pickle.dump(self.model, f)

        # Save metadata
        metadata = {
            "model_type": self.model_type,
            "metrics": self.metrics,
            "feature_importance": self.feature_importance,
            "timestamp": datetime.now().isoformat(),
        }
        with open(f"{path}_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Model saved to {path}")

    def load(self, path: Optional[str] = None) -> None:
        """Load model from disk"""
        path = path or self.model_path

        try:
            with open(f"{path}.pkl", "rb") as f:
                self.model = pickle.load(f)

            with open(f"{path}_metadata.json", "r") as f:
                metadata = json.load(f)
                self.metrics = metadata.get("metrics", {})
                self.feature_importance = metadata.get("feature_importance", {})

            logger.info(f"Model loaded from {path}")
        except FileNotFoundError as e:
            raise ModelNotFoundError(f"Model not found at {path}: {str(e)}")