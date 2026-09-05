from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.base import Base
import uuid


class Store(Base):
    __tablename__ = "stores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    address = Column(Text)
    city = Column(String(100), nullable=False, index=True)
    province = Column(String(100))
    region = Column(String(50))
    store_type = Column(String(50))  # Supermarket, Hypermarket, etc.
    floor_area_sqm = Column(Float)
    parking_capacity = Column(Integer)
    opening_hours = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    inventory = relationship("Inventory", back_populates="store")
    transactions = relationship("Transaction", back_populates="store")

    def __repr__(self):
        return f"<Store(code='{self.code}', name='{self.name}')>"