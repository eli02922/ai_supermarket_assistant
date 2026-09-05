from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.base import Base
import uuid


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100))
    brand = Column(String(100))
    unit_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)
    weight_kg = Column(Float)
    is_perishable = Column(Boolean, default=False)
    shelf_life_days = Column(Integer)
    reorder_point = Column(Integer)
    reorder_quantity = Column(Integer)
    lead_time_days = Column(Integer, default=3)
    supplier = Column(String(100))
    supplier_contact = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    inventory = relationship("Inventory", back_populates="product")
    transactions = relationship("Transaction", back_populates="product")
    forecasts = relationship("Forecast", back_populates="product")

    def __repr__(self):
        return f"<Product(sku='{self.sku}', name='{self.name}')>"