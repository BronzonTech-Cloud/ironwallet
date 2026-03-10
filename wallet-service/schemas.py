from datetime import datetime

from pydantic import BaseModel


class WalletCreate(BaseModel):
    user_id: int
    currency: str = "USD"


class WalletResponse(BaseModel):
    id: int
    user_id: int
    balance: float
    currency: str
    is_frozen: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WalletUpdate(BaseModel):
    is_frozen: bool
