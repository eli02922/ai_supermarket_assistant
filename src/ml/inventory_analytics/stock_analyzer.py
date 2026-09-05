from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.data.models.inventory import Inventory
from src.data.models.transaction import Transaction
from src.data.models.product import Product
from src.core.logging import get_logger
from src.core.exceptions import ForecastError

logger = get_logger(__name__)


class StockAnalyzer:
    """Inventory stock analysis"""

    def __init__(self):
        self.db = next(get_db())

    def detect_stockouts(
        self,
        days_ahead: int = 7,
        threshold_percentage: float = 0.2,
    ) -> List[Dict[str, Any]]:
        """Detect products likely to stock out"""
        logger.info("Detecting potential stockouts...")

        try:
            # Get current inventory
            inventory = self._get_current_inventory()

            # Get daily sales rates
            sales_rates = self._get_daily_sales_rates()

            stockout_risk = []

            for item in inventory:
                product_id = item["product_id"]
                store_id = item["store_id"]
                current_stock = item["quantity_on_hand"]

                daily_sales = sales_rates.get((product_id, store_id), 0)
                if daily_sales == 0:
                    continue

                # Days until stockout
                days_until_stockout = current_stock / daily_sales

                if days_until_stockout <= days_ahead:
                    stockout_risk.append({
                        "product_id": product_id,
                        "store_id": store_id,
                        "product_name": item["product_name"],
                        "store_name": item["store_name"],
                        "current_stock": current_stock,
                        "daily_sales": daily_sales,
                        "days_until_stockout": days_until_stockout,
                        "risk_level": self._calculate_risk_level(
                            days_until_stockout, days_ahead
                        ),
                    })

            # Sort by days until stockout
            stockout_risk.sort(key=lambda x: x["days_until_stockout"])

            logger.info(f"Found {len(stockout_risk)} products at risk of stockout")
            return stockout_risk

        except Exception as e:
            logger.error(f"Error detecting stockouts: {str(e)}")
            raise ForecastError(f"Stockout detection failed: {str(e)}")

    def identify_slow_moving_products(
        self,
        days_lookback: int = 30,
        threshold_sales: int = 10,
    ) -> List[Dict[str, Any]]:
        """Identify slow-moving products"""
        logger.info("Identifying slow-moving products...")

        try:
            cutoff_date = datetime.now() - timedelta(days=days_lookback)

            # Get product sales data
            sales_data = (
                self.db.query(
                    Product.id,
                    Product.name,
                    Product.category,
                    Transaction.product_id,
                    Transaction.store_id,
                )
                .join(Transaction, Transaction.product_id == Product.id)
                .filter(Transaction.date >= cutoff_date.date())
                .all()
            )

            # Aggregate sales by product
            df = pd.DataFrame([{
                "product_id": s.product_id,
                "store_id": s.store_id,
                "product_name": s.name,
                "category": s.category,
                "total_quantity": 1,
            } for s in sales_data])

            if df.empty:
                return []

            # Group by product
            product_sales = df.groupby(
                ["product_id", "product_name", "category"]
            ).agg({
                "total_quantity": "sum",
                "store_id": "nunique",
            }).reset_index()

            product_sales.columns = [
                "product_id", "product_name", "category",
                "total_quantity", "store_count"
            ]

            # Filter slow-moving products
            slow_moving = product_sales[
                product_sales["total_quantity"] <= threshold_sales
            ].to_dict("records")

            logger.info(f"Found {len(slow_moving)} slow-moving products")
            return slow_moving

        except Exception as e:
            logger.error(f"Error identifying slow-moving products: {str(e)}")
            raise

    def identify_fast_moving_products(
        self,
        days_lookback: int = 30,
        threshold_percentile: float = 0.9,
    ) -> List[Dict[str, Any]]:
        """Identify fast-moving products"""
        logger.info("Identifying fast-moving products...")

        try:
            cutoff_date = datetime.now() - timedelta(days=days_lookback)

            # Get product sales data
            sales_data = (
                self.db.query(
                    Product.id,
                    Product.name,
                    Product.category,
                    Transaction.product_id,
                    Transaction.store_id,
                )
                .join(Transaction, Transaction.product_id == Product.id)
                .filter(Transaction.date >= cutoff_date.date())
                .all()
            )

            # Aggregate sales by product
            df = pd.DataFrame([{
                "product_id": s.product_id,
                "store_id": s.store_id,
                "product_name": s.name,
                "category": s.category,
                "total_quantity": 1,
            } for s in sales_data])

            if df.empty:
                return []

            # Group by product
            product_sales = df.groupby(
                ["product_id", "product_name", "category"]
            ).agg({
                "total_quantity": "sum",
                "store_id": "nunique",
            }).reset_index()

            product_sales.columns = [
                "product_id", "product_name", "category",
                "total_quantity", "store_count"
            ]

            # Get threshold
            threshold = product_sales["total_quantity"].quantile(threshold_percentile)

            # Filter fast-moving products
            fast_moving = product_sales[
                product_sales["total_quantity"] >= threshold
            ].to_dict("records")

            # Sort by quantity
            fast_moving.sort(key=lambda x: x["total_quantity"], reverse=True)

            logger.info(f"Found {len(fast_moving)} fast-moving products")
            return fast_moving

        except Exception as e:
            logger.error(f"Error identifying fast-moving products: {str(e)}")
            raise

    def _get_current_inventory(self) -> List[Dict[str, Any]]:
        """Get current inventory levels"""
        today = datetime.now().date()

        inventory = (
            self.db.query(
                Inventory.product_id,
                Inventory.store_id,
                Inventory.quantity_on_hand,
                Product.name.label("product_name"),
                Store.name.label("store_name"),
            )
            .join(Product, Inventory.product_id == Product.id)
            .join(Store, Inventory.store_id == Store.id)
            .filter(Inventory.date == today)
            .all()
        )

        return [
            {
                "product_id": item.product_id,
                "store_id": item.store_id,
                "quantity_on_hand": item.quantity_on_hand,
                "product_name": item.product_name,
                "store_name": item.store_name,
            }
            for item in inventory
        ]

    def _get_daily_sales_rates(self) -> Dict[tuple, float]:
        """Get average daily sales rates for products"""
        days_lookback = 30
        cutoff_date = datetime.now() - timedelta(days=days_lookback)

        sales = (
            self.db.query(
                Transaction.product_id,
                Transaction.store_id,
                Transaction.quantity,
            )
            .filter(Transaction.date >= cutoff_date.date())
            .all()
        )

        sales_rates = {}
        for s in sales:
            key = (s.product_id, s.store_id)
            sales_rates[key] = sales_rates.get(key, 0) + s.quantity

        # Calculate daily average
        for key in sales_rates:
            sales_rates[key] = sales_rates[key] / days_lookback

        return sales_rates

    def _calculate_risk_level(
        self, days_until_stockout: float, days_ahead: int
    ) -> str:
        """Calculate risk level based on days until stockout"""
        ratio = days_until_stockout / days_ahead
        if ratio < 0.3:
            return "critical"
        elif ratio < 0.6:
            return "high"
        elif ratio < 0.9:
            return "medium"
        else:
            return "low"