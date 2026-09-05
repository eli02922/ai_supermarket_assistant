from typing import List, Dict, Any
from datetime import datetime
from src.core.logging import get_logger
from src.core.exceptions import DataValidationError

logger = get_logger(__name__)


class DataValidator:
    """Validator for supermarket data"""

    def validate_products(self, products: List[Dict[str, Any]]) -> None:
        """Validate product data"""
        if not products:
            raise DataValidationError("No products provided")

        required_fields = ["sku", "name", "category", "unit_price", "cost_price"]

        for i, product in enumerate(products):
            # Check required fields
            for field in required_fields:
                if field not in product:
                    raise DataValidationError(
                        f"Product {i}: Missing required field '{field}'"
                    )

            # Validate numeric fields
            if product["unit_price"] <= 0:
                raise DataValidationError(f"Product {i}: Unit price must be positive")

            if product["cost_price"] <= 0:
                raise DataValidationError(f"Product {i}: Cost price must be positive")

            if product["cost_price"] > product["unit_price"]:
                raise DataValidationError(
                    f"Product {i}: Cost price cannot exceed unit price"
                )

            # Validate SKU format
            if not product["sku"].startswith("PRD"):
                raise DataValidationError(
                    f"Product {i}: Invalid SKU format - should start with 'PRD'"
                )

        logger.info(f"Validated {len(products)} products")

    def validate_stores(self, stores: List[Dict[str, Any]]) -> None:
        """Validate store data"""
        if not stores:
            raise DataValidationError("No stores provided")

        required_fields = ["code", "name", "city"]

        for i, store in enumerate(stores):
            for field in required_fields:
                if field not in store:
                    raise DataValidationError(
                        f"Store {i}: Missing required field '{field}'"
                    )

            if len(store["code"]) < 3:
                raise DataValidationError(
                    f"Store {i}: Store code must be at least 3 characters"
                )

        logger.info(f"Validated {len(stores)} stores")

    def validate_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """Validate transaction data"""
        if not transactions:
            raise DataValidationError("No transactions provided")

        required_fields = ["transaction_id", "store_id", "product_id", "date", "quantity", "total_amount"]

        for i, tx in enumerate(transactions):
            for field in required_fields:
                if field not in tx:
                    raise DataValidationError(
                        f"Transaction {i}: Missing required field '{field}'"
                    )

            # Validate quantity
            if tx["quantity"] <= 0:
                raise DataValidationError(
                    f"Transaction {i}: Quantity must be positive"
                )

            # Validate amount
            if tx["total_amount"] <= 0:
                raise DataValidationError(
                    f"Transaction {i}: Total amount must be positive"
                )

            # Validate date
            try:
                datetime.strptime(tx["date"], "%Y-%m-%d")
            except ValueError:
                raise DataValidationError(
                    f"Transaction {i}: Invalid date format - should be YYYY-MM-DD"
                )

        logger.info(f"Validated {len(transactions)} transactions")

    def validate_inventory(self, inventory: List[Dict[str, Any]]) -> None:
        """Validate inventory data"""
        if not inventory:
            raise DataValidationError("No inventory records provided")

        required_fields = ["store_id", "product_id", "date", "quantity_on_hand"]

        for i, inv in enumerate(inventory):
            for field in required_fields:
                if field not in inv:
                    raise DataValidationError(
                        f"Inventory {i}: Missing required field '{field}'"
                    )

            if inv["quantity_on_hand"] < 0:
                raise DataValidationError(
                    f"Inventory {i}: Quantity on hand cannot be negative"
                )

        logger.info(f"Validated {len(inventory)} inventory records")