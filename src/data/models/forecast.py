from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.base import Base
import uuid


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    store_id = Column(String(36), ForeignKey("stores.id"), nullable=True, index=True)
    forecast_date = Column(Date, nullable=False, index=True)
    horizon_days = Column(Integer, nullable=False)
    demand_prediction = Column(Float, nullable=False)
    demand_lower_bound = Column(Float)
    demand_upper_bound = Column(Float)
    confidence_level = Column(Float, default=0.95)
    model_version = Column(String(50))
    features_used = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="forecasts")

    def __repr__(self):
        return f"<Forecast(product='{self.product_id}', date='{self.forecast_date}')>"