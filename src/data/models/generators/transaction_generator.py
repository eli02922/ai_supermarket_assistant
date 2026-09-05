from typing import List, Dict, Any, Optional
import random
import pandas as pd
from datetime import datetime, timedelta
from .base_generator import BaseDataGenerator
from src.core.logging import get_logger

logger = get_logger(__name__)


class TransactionGenerator(BaseDataGenerator):
    """Transaction data generator"""

    def __init__(
        self,
        product_ids: List[str],
        store_ids: List[str],
        start_date: datetime,
        end_date: datetime,
        num_transactions: int = 100000,
        seed: Optional[int] = None,
    ):
        super().__init__(seed)
        self.product_ids = product_ids
        self.store_ids = store_ids
        self.start_date = start_date
        self.end_date = end_date
        self.num_transactions = num_transactions

    def generate_batch(
        self, batch_size: int = 10000, **kwargs
    ) -> List[Dict[str, Any]]:
        """Generate transaction records"""
        transactions = []
        remaining = min(batch_size, self.num_transactions - len(transactions) if transactions else 0)

        for _ in range(remaining):
            date = self._random_date(self.start_date, self.end_date)
            # Add seasonality patterns
            date = self._apply_seasonality(date)

            store_id = random.choice(self.store_ids)
            product_id = random.choice(self.product_ids)

            # Random quantity with some bias
            quantity = self._generate_quantity()
            unit_price = random.uniform(10, 5000)  # Will be overwritten by actual product price
            total_amount = quantity * unit_price
            discount = random.choice([0, 0.05, 0.10, 0.15, 0.20]) * total_amount
            tax = 0.12 * (total_amount - discount)

            transaction = {
                "id": self._generate_id(),
                "transaction_id": f"TXN{random.randint(100000, 999999)}",
                "store_id": store_id,
                "product_id": product_id,
                "date": date.strftime("%Y-%m-%d"),
                "time": self._random_time().strftime("%H:%M:%S"),
                "quantity": quantity,
                "unit_price": round(unit_price, 2),
                "total_amount": round(total_amount, 2),
                "discount": round(discount, 2),
                "tax": round(tax, 2),
                "payment_method": random.choice(["Cash", "Credit Card", "Debit Card", "Mobile Payment"]),
                "customer_id": f"CUST{random.randint(10000, 99999)}",
                "is_return": 0,
            }
            transactions.append(transaction)

        logger.info(f"Generated {len(transactions)} transactions")
        return transactions

    def _apply_seasonality(self, date: datetime) -> datetime:
        """Apply seasonality patterns to dates"""
        # Weekend effect
        if date.weekday() >= 5:  # Weekend
            date += timedelta(days=random.randint(-1, 1))

        # Holiday effects (simplified)
        if date.month == 12 and date.day >= 15:
            date += timedelta(days=random.randint(-3, 3))
        if date.month == 1 and date.day <= 5:
            date += timedelta(days=random.randint(-2, 2))

        return date

    def _random_time(self) -> datetime:
        """Generate random time within store hours (8 AM - 9 PM)"""
        hour = random.randint(8, 20)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return datetime(2024, 1, 1, hour, minute, second)

    def _generate_quantity(self) -> int:
        """Generate quantity with realistic distribution"""
        weights = [0.6, 0.25, 0.1, 0.04, 0.01]
        values = [1, 2, 3, 4, 5]
        base_quantity = random.choices(values, weights=weights)[0]

        # Add random variation
        if random.random() < 0.3:
            base_quantity += random.randint(1, 3)

        return base_quantity