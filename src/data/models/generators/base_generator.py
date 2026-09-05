import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from faker import Faker
from src.core.logging import get_logger

logger = get_logger(__name__)
fake = Faker()


class BaseDataGenerator:
    """Base class for data generators"""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            Faker.seed(seed)

    def generate_batch(
        self, batch_size: int = 1000, **kwargs
    ) -> List[Dict[str, Any]]:
        """Generate a batch of records"""
        raise NotImplementedError

    def _random_date(
        self, start_date: datetime, end_date: datetime
    ) -> datetime:
        """Generate random date between start and end"""
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randint(0, days_between)
        return start_date + timedelta(days=random_days)

    def _generate_id(self) -> str:
        """Generate a random ID"""
        return fake.uuid4()

    def _generate_sku(self, prefix: str = "SKU") -> str:
        """Generate a SKU"""
        return f"{prefix}{random.randint(10000, 99999)}"