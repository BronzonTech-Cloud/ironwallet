from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from shared.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # DEPOSIT, WITHDRAW, TRANSFER
    from_wallet = Column(Integer, nullable=True)
    to_wallet = Column(Integer, nullable=True)
    amount = Column(Float)
    fee = Column(Float, default=0.0)
    status = Column(String, default="PENDING")  # PENDING, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)
