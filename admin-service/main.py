import os
from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
    text,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker

app = FastAPI()

# Database Connections
AUTH_DB_URL = os.getenv("DATABASE_URL_AUTH")
WALLET_DB_URL = os.getenv("DATABASE_URL_WALLET")
TXN_DB_URL = os.getenv("DATABASE_URL_TRANSACTION")

engine_auth = create_engine(AUTH_DB_URL)
engine_wallet = create_engine(WALLET_DB_URL)
engine_txn = create_engine(TXN_DB_URL)

SessionAuth = sessionmaker(bind=engine_auth)
SessionWallet = sessionmaker(bind=engine_wallet)
SessionTxn = sessionmaker(bind=engine_txn)


def get_auth_db():
    db = SessionAuth()
    try:
        yield db
    finally:
        db.close()


def get_wallet_db():
    db = SessionWallet()
    try:
        yield db
    finally:
        db.close()


def get_txn_db():
    db = SessionTxn()
    try:
        yield db
    finally:
        db.close()


# Simple Models for Admin (mirroring others)
Base = declarative_base()


class AdminUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String)
    is_active = Column(Boolean)


class AdminWallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    balance = Column(Float)
    is_frozen = Column(Boolean)


class AdminTransaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    type = Column(String)
    amount = Column(Float)
    status = Column(String)
    created_at = Column(DateTime)


# Schemas
class BanRequest(BaseModel):
    user_id: int
    is_active: bool


class FreezeRequest(BaseModel):
    wallet_id: int
    is_frozen: bool


class BalanceRequest(BaseModel):
    wallet_id: int
    new_balance: float


@app.post("/admin/user/ban")
def ban_user(req: BanRequest, db: Session = Depends(get_auth_db)):
    user = db.query(AdminUser).filter(AdminUser.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = req.is_active
    db.commit()
    return {"message": "User status updated"}


@app.post("/admin/wallet/freeze")
def freeze_wallet(req: FreezeRequest, db: Session = Depends(get_wallet_db)):
    wallet = db.query(AdminWallet).filter(AdminWallet.id == req.wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    wallet.is_frozen = req.is_frozen
    db.commit()
    return {"message": "Wallet status updated"}


@app.post("/admin/wallet/adjust_balance")
def adjust_balance(req: BalanceRequest, db: Session = Depends(get_wallet_db)):
    wallet = db.query(AdminWallet).filter(AdminWallet.id == req.wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    # In a real system, you'd insert a transaction record too!
    wallet.balance = req.new_balance
    db.commit()
    return {"message": "Balance updated"}


@app.get("/admin/transactions")
def view_transactions(db: Session = Depends(get_txn_db)):
    txs = db.query(AdminTransaction).limit(100).all()
    return txs
