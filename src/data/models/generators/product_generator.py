from typing import List, Dict, Any, Optional
import random
from .base_generator import BaseDataGenerator
from src.core.logging import get_logger

logger = get_logger(__name__)


class ProductGenerator(BaseDataGenerator):
    """Product data generator"""

    def __init__(self, num_products: int = 1000, seed: Optional[int] = None):
        super().__init__(seed)
        self.num_products = num_products

        self.categories = {
            "Beverages": {
                "subcategories": ["Soft Drinks", "Juices", "Water", "Energy Drinks", "Coffee", "Tea"],
                "brands": ["Coca-Cola", "Pepsi", "Nestle", "Starbucks", "Nescafe", "Lipton"]
            },
            "Food": {
                "subcategories": ["Canned Goods", "Pasta", "Rice", "Cereals", "Snacks", "Condiments"],
                "brands": ["Del Monte", "San Miguel", "Jollibee", "Knorr", "Ajinomoto", "Meadow"]
            },
            "Dairy": {
                "subcategories": ["Milk", "Cheese", "Yogurt", "Butter", "Eggs"],
                "brands": ["Alaska", "Nestle", "Magnolia", "Arla", "Anchor"]
            },
            "Meat": {
                "subcategories": ["Chicken", "Pork", "Beef", "Seafood", "Processed Meat"],
                "brands": ["Magnolia", "San Miguel", "Purefoods", "Tender Juicy"]
            },
            "Produce": {
                "subcategories": ["Fruits", "Vegetables", "Herbs"],
                "brands": ["Fresh", "Organic", "Local"]
            },
            "Household": {
                "subcategories": ["Cleaning", "Laundry", "Paper Products", "Kitchen"],
                "brands": ["Tide", "Surf", "Downy", "Zonrox", "Joy"]
            },
            "Personal Care": {
                "subcategories": ["Shampoo", "Soap", "Toothpaste", "Skincare", "Deodorant"],
                "brands": ["Safeguard", "Colgate", "Head & Shoulders", "Pantene", "Dove"]
            },
            "Baby Care": {
                "subcategories": ["Diapers", "Formula", "Baby Food", "Toiletries"],
                "brands": ["Pampers", "Huggies", "Similac", "Nestle"]
            }
        }

    def generate_batch(
        self, batch_size: int = 100, **kwargs
    ) -> List[Dict[str, Any]]:
        """Generate product records"""
        products = []
        categories = list(self.categories.keys())

        for i in range(min(batch_size, self.num_products - len(products) if products else 0)):
            category = random.choice(categories)
            subcategories = self.categories[category]["subcategories"]
            brands = self.categories[category]["brands"]

            subcategory = random.choice(subcategories)
            brand = random.choice(brands)

            is_perishable = random.choice([True, False])
            shelf_life = random.randint(7, 365) if is_perishable else random.randint(30, 730)

            unit_price = round(random.uniform(10, 5000), 2)
            cost_price = round(unit_price * random.uniform(0.4, 0.8), 2)

            product = {
                "id": self._generate_id(),
                "sku": self._generate_sku(f"PRD"),
                "name": f"{brand} {self._generate_product_name(category, subcategory)}",
                "category": category,
                "subcategory": subcategory,
                "brand": brand,
                "unit_price": unit_price,
                "cost_price": cost_price,
                "weight_kg": round(random.uniform(0.1, 10), 2),
                "is_perishable": is_perishable,
                "shelf_life_days": shelf_life,
                "reorder_point": random.randint(5, 100),
                "reorder_quantity": random.randint(10, 200),
                "lead_time_days": random.randint(1, 14),
                "supplier": self._generate_supplier(category),
                "supplier_contact": fake.phone_number(),
                "description": fake.sentence(nb_words=10)
            }
            products.append(product)

        logger.info(f"Generated {len(products)} products")
        return products

    def _generate_product_name(self, category: str, subcategory: str) -> str:
        """Generate a product name"""
        adjectives = ["Premium", "Classic", "Organic", "Natural", "Essential", "Deluxe", "Original"]
        return f"{random.choice(adjectives)} {subcategory}"

    def _generate_supplier(self, category: str) -> str:
        """Generate supplier name"""
        suppliers = {
            "Beverages": ["Beverage Distributors Inc", "Drinks Supply Co", "Pure Water Corp"],
            "Food": ["Food Suppliers Inc", "Quality Foods", "Fresh Food Distributors"],
            "Dairy": ["Dairy Products Inc", "Milk Supply Co", "Dairy Farm"],
            "Meat": ["Meat Suppliers Inc", "Poultry Farm", "Meat Processing Co"],
            "Produce": ["Fresh Produce Inc", "Fruit Distributors", "Vegetable Supply"],
            "Household": ["Household Supplies", "Home Products Inc", "Cleaning Solutions"],
            "Personal Care": ["Beauty Supplies Inc", "Personal Care Distributors"],
            "Baby Care": ["Baby Products Inc", "Child Care Supplies"]
        }
        return random.choice(suppliers.get(category, ["General Supplies"]))