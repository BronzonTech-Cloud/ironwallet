from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from shared.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    balance = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    is_frozen = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
