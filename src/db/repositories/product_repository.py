from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from src.data.models.product import Product
from src.data.models.transaction import Transaction
from src.db.session import get_db
from src.core.logging import get_logger

logger = get_logger(__name__)


class ProductRepository:
    """Repository for product operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        return self.db.query(Product).filter(Product.sku == sku).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        brand: Optional[str] = None,
    ) -> List[Product]:
        """Get all products with filters"""
        query = self.db.query(Product)

        if category:
            query = query.filter(Product.category == category)
        if brand:
            query = query.filter(Product.brand == brand)

        return query.offset(skip).limit(limit).all()

    def create(self, product_data: Dict[str, Any]) -> Product:
        """Create a new product"""
        product = Product(**product_data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product_id: str, product_data: Dict[str, Any]) -> Optional[Product]:
        """Update a product"""
        product = self.get_by_id(product_id)
        if not product:
            return None

        for key, value in product_data.items():
            setattr(product, key, value)

        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: str) -> bool:
        """Delete a product"""
        product = self.get_by_id(product_id)
        if not product:
            return False

        self.db.delete(product)
        self.db.commit()
        return True

    def get_sales_summary(
        self,
        product_id: str,
        days_lookback: int = 30,
    ) -> Dict[str, Any]:
        """Get sales summary for a product"""
        product = self.get_by_id(product_id)
        if not product:
            return {}

        # Get sales data
        sales = (
            self.db.query(
                func.sum(Transaction.quantity).label("total_quantity"),
                func.sum(Transaction.total_amount).label("total_revenue"),
                func.count(Transaction.id).label("transaction_count"),
                func.avg(Transaction.quantity).label("avg_quantity"),
                func.avg(Transaction.unit_price).label("avg_price"),
            )
            .filter(Transaction.product_id == product_id)
            .filter(Transaction.date >= func.current_date() - func.interval(f"{days_lookback} days"))
            .first()
        )

        return {
            "product_id": product_id,
            "product_name": product.name,
            "sku": product.sku,
            "category": product.category,
            "unit_price": product.unit_price,
            "total_quantity": sales.total_quantity or 0,
            "total_revenue": sales.total_revenue or 0,
            "transaction_count": sales.transaction_count or 0,
            "avg_quantity": sales.avg_quantity or 0,
            "avg_price": sales.avg_price or 0,
        }