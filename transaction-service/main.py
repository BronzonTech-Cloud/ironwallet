import os

import httpx
import models
import schemas
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from shared.config import settings
from shared.database import Base, get_db_engine, get_db_session
from shared.logging_utils import get_logger
from shared.messaging import publish_event

logger = get_logger("transaction-service")

app = FastAPI()

# Database Setup
engine = get_db_engine(settings.DATABASE_URL)
models.Base.metadata.create_all(bind=engine)

WALLET_SERVICE_URL = os.getenv("WALLET_SERVICE_URL", "http://wallet-service:8000")


async def update_wallet_balance(wallet_id: int, amount: float):
    # Call Wallet Service
    async with httpx.AsyncClient() as client:
        try:
            # We call the internal endpoint
            response = await client.post(
                f"{WALLET_SERVICE_URL}/wallet/internal/update_balance",
                params={"wallet_id": wallet_id, "amount": amount},
            )
            if response.status_code != 200:
                logger.error(f"Failed to update wallet {wallet_id}: {response.text}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error calling wallet service: {e}")
            return False


@app.post("/transaction/send", response_model=schemas.TransactionResponse)
async def send_money(
    tx: schemas.TransactionCreate,
    db: Session = Depends(lambda: next(get_db_session(engine))),
):
    if tx.type != "TRANSFER":
        raise HTTPException(
            status_code=400, detail="Invalid transaction type for this endpoint"
        )
    if not tx.from_wallet or not tx.to_wallet:
        raise HTTPException(
            status_code=400, detail="Source and destination wallets required"
        )
    if tx.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # 1. Create Transaction Record (PENDING)
    new_tx = models.Transaction(
        type="TRANSFER",
        from_wallet=tx.from_wallet,
        to_wallet=tx.to_wallet,
        amount=tx.amount,
        status="PENDING",
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    # 2. Debit Sender
    # Using negative amount
    success_sender = await update_wallet_balance(tx.from_wallet, -tx.amount)
    if not success_sender:
        new_tx.status = "FAILED"
        db.commit()
        raise HTTPException(
            status_code=400, detail="Sender has insufficient funds or wallet frozen"
        )

    # 3. Credit Receiver
    success_receiver = await update_wallet_balance(tx.to_wallet, tx.amount)
    if not success_receiver:
        # Critical Failure: Money left sender but didn't reach receiver.
        # Must Refund Sender (Compensating Transaction)
        logger.error(f"Transaction {new_tx.id} partially failed. Refunding sender.")
        await update_wallet_balance(tx.from_wallet, tx.amount)
        new_tx.status = "FAILED"
        db.commit()
        raise HTTPException(
            status_code=500, detail="Transaction failed during processing"
        )

    # 4. Success
    new_tx.status = "COMPLETED"
    db.commit()

    publish_event(
        "transaction.completed",
        {
            "id": new_tx.id,
            "from": tx.from_wallet,
            "to": tx.to_wallet,
            "amount": tx.amount,
        },
    )

    return new_tx


@app.post("/transaction/deposit", response_model=schemas.TransactionResponse)
async def deposit(
    tx: schemas.TransactionCreate,
    db: Session = Depends(lambda: next(get_db_session(engine))),
):
    if tx.type != "DEPOSIT":
        raise HTTPException(status_code=400, detail="Invalid type")
    if not tx.to_wallet:
        raise HTTPException(status_code=400, detail="Destination wallet required")

    new_tx = models.Transaction(
        type="DEPOSIT", to_wallet=tx.to_wallet, amount=tx.amount, status="PENDING"
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    if await update_wallet_balance(tx.to_wallet, tx.amount):
        new_tx.status = "COMPLETED"
        db.commit()
        publish_event(
            "transaction.completed",
            {"id": new_tx.id, "type": "DEPOSIT", "amount": tx.amount},
        )
        return new_tx
    else:
        new_tx.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=400, detail="Deposit failed")


@app.post("/transaction/withdraw", response_model=schemas.TransactionResponse)
async def withdraw(
    tx: schemas.TransactionCreate,
    db: Session = Depends(lambda: next(get_db_session(engine))),
):
    if tx.type != "WITHDRAW":
        raise HTTPException(status_code=400, detail="Invalid type")
    if not tx.from_wallet:
        raise HTTPException(status_code=400, detail="Source wallet required")

    new_tx = models.Transaction(
        type="WITHDRAW", from_wallet=tx.from_wallet, amount=tx.amount, status="PENDING"
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    if await update_wallet_balance(tx.from_wallet, -tx.amount):
        new_tx.status = "COMPLETED"
        db.commit()
        publish_event(
            "transaction.completed",
            {"id": new_tx.id, "type": "WITHDRAW", "amount": tx.amount},
        )
        return new_tx
    else:
        new_tx.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=400, detail="Withdrawal failed")


@app.get("/transaction/history/{wallet_id}")
def get_history(
    wallet_id: int, db: Session = Depends(lambda: next(get_db_session(engine)))
):
    # Find all transactions where from_wallet OR to_wallet is wallet_id
    from sqlalchemy import or_

    txs = (
        db.query(models.Transaction)
        .filter(
            or_(
                models.Transaction.from_wallet == wallet_id,
                models.Transaction.to_wallet == wallet_id,
            )
        )
        .all()
    )
    return txs
