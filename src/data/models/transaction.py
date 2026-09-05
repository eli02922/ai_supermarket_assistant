from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from src.db.base import Base
import uuid


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(50), unique=True, nullable=False, index=True)
    store_id = Column(String(36), ForeignKey("stores.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    time = Column(Time)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    discount = Column(Float, default=0)
    tax = Column(Float, default=0)
    payment_method = Column(String(50))
    customer_id = Column(String(50))
    is_return = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    store = relationship("Store", back_populates="transactions")
    product = relationship("Product", back_populates="transactions")

    @hybrid_property
    def net_amount(self):
        return self.total_amount - self.discount + self.tax

    def __repr__(self):
        return f"<Transaction(id='{self.transaction_id}', date='{self.date}')>"