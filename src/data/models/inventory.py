from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.base import Base
import uuid


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id = Column(String(36), ForeignKey("stores.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    quantity_on_hand = Column(Integer, nullable=False)
    quantity_reserved = Column(Integer, default=0)
    quantity_ordered = Column(Integer, default=0)
    reorder_point = Column(Integer)
    reorder_quantity = Column(Integer)
    lead_time_days = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    store = relationship("Store", back_populates="inventory")
    product = relationship("Product", back_populates="inventory")

    @property
    def available_quantity(self):
        return self.quantity_on_hand - self.quantity_reserved

    def __repr__(self):
        return f"<Inventory(store='{self.store_id}', product='{self.product_id}')>"