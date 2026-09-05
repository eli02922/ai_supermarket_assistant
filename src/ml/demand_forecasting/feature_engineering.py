import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Any
from sklearn.preprocessing import StandardScaler
from src.core.logging import get_logger

logger = get_logger(__name__)


class FeatureEngineer:
    """Feature engineering for demand forecasting"""

    def __init__(self):
        self.scaler = StandardScaler()

    def create_features(
        self,
        df: pd.DataFrame,
        target_col: str = "quantity",
        date_col: str = "date",
    ) -> pd.DataFrame:
        """Create features for demand forecasting"""
        df = df.copy()

        # Ensure date is datetime
        df[date_col] = pd.to_datetime(df[date_col])

        # Time-based features
        df["year"] = df[date_col].dt.year
        df["month"] = df[date_col].dt.month
        df["day"] = df[date_col].dt.day
        df["day_of_week"] = df[date_col].dt.dayofweek
        df["quarter"] = df[date_col].dt.quarter
        df["week_of_year"] = df[date_col].dt.isocalendar().week
        df["day_of_year"] = df[date_col].dt.dayofyear
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

        # Cyclical encoding
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
        df["day_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["day_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

        # Lag features
        df = self._create_lag_features(df, target_col)
        df = self._create_rolling_features(df, target_col)
        df = self._create_holiday_features(df, date_col)

        # Seasonal features
        df = self._create_seasonal_features(df)

        # Drop rows with NaN values
        df = df.dropna()

        logger.info(f"Created {len(df.columns)} features")
        return df

    def _create_lag_features(
        self, df: pd.DataFrame, target_col: str
    ) -> pd.DataFrame:
        """Create lag features"""
        for lag in [1, 3, 7, 14, 30]:
            df[f"{target_col}_lag_{lag}"] = df[target_col].shift(lag)
        return df

    def _create_rolling_features(
        self, df: pd.DataFrame, target_col: str
    ) -> pd.DataFrame:
        """Create rolling statistics features"""
        for window in [7, 14, 30]:
            df[f"{target_col}_rolling_mean_{window}"] = (
                df[target_col].rolling(window).mean()
            )
            df[f"{target_col}_rolling_std_{window}"] = (
                df[target_col].rolling(window).std()
            )
            df[f"{target_col}_rolling_min_{window}"] = (
                df[target_col].rolling(window).min()
            )
            df[f"{target_col}_rolling_max_{window}"] = (
                df[target_col].rolling(window).max()
            )
        return df

    def _create_holiday_features(
        self, df: pd.DataFrame, date_col: str
    ) -> pd.DataFrame:
        """Create holiday features"""
        holidays = [
            ("2024-01-01", "New Year"),
            ("2024-02-14", "Valentines"),
            ("2024-04-01", "Easter"),
            ("2024-05-01", "Labor Day"),
            ("2024-06-12", "Independence Day"),
            ("2024-08-25", "National Heroes Day"),
            ("2024-11-01", "All Saints Day"),
            ("2024-11-30", "Bonifacio Day"),
            ("2024-12-25", "Christmas"),
            ("2024-12-31", "New Year Eve"),
            ("2025-01-01", "New Year"),
            ("2025-02-14", "Valentines"),
            ("2025-04-20", "Easter"),
            ("2025-05-01", "Labor Day"),
            ("2025-06-12", "Independence Day"),
            ("2025-08-31", "National Heroes Day"),
            ("2025-11-01", "All Saints Day"),
            ("2025-11-30", "Bonifacio Day"),
            ("2025-12-25", "Christmas"),
            ("2025-12-31", "New Year Eve"),
        ]

        df["is_holiday"] = 0
        df["holiday_name"] = None

        for date, name in holidays:
            holiday_date = pd.to_datetime(date)
            df.loc[df[date_col].dt.date == holiday_date.date(), "is_holiday"] = 1
            df.loc[df[date_col].dt.date == holiday_date.date(), "holiday_name"] = name

        return df

    def _create_seasonal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create seasonal features"""
        # Quarter of year
        df["quarter_of_year"] = df["quarter"]

        # Month of year (seasonality)
        df["month_of_year"] = df["month"]

        # Week of year
        df["week_of_year"] = df["week_of_year"]

        # Day of year (seasonality)
        df["day_of_year"] = df["day_of_year"]

        return df

    def prepare_features(
        self,
        df: pd.DataFrame,
        target_col: str = "quantity",
        date_col: str = "date",
        scale: bool = True,
    ) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """Prepare features for training"""
        df = self.create_features(df, target_col, date_col)

        # Exclude non-feature columns
        exclude_cols = ["date", "store_id", "product_id", "transaction_id", "id"]
        feature_cols = [col for col in df.columns if col not in exclude_cols]

        X = df[feature_cols]
        y = df[target_col] if target_col in df.columns else None

        if scale:
            X_scaled = pd.DataFrame(
                self.scaler.fit_transform(X),
                columns=X.columns,
                index=X.index,
            )
            return X_scaled, y, feature_cols

        return X, y, feature_cols