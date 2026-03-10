from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TransactionCreate(BaseModel):
    type: str  # DEPOSIT, WITHDRAW, TRANSFER
    from_wallet: Optional[int] = None
    to_wallet: Optional[int] = None
    amount: float


class TransactionResponse(BaseModel):
    id: int
    type: str
    from_wallet: Optional[int]
    to_wallet: Optional[int]
    amount: float
    fee: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
