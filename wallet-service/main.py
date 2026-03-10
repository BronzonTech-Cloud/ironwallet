import models
import redis
import schemas
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from shared.config import settings
from shared.database import Base, get_db_engine, get_db_session
from shared.logging_utils import get_logger
from shared.messaging import publish_event

logger = get_logger("wallet-service")

app = FastAPI()

# Database Setup
engine = get_db_engine(settings.DATABASE_URL)
models.Base.metadata.create_all(bind=engine)

# Redis for Locking (Simpler than full Redlock for this scope, but good practice)
redis_client = redis.Redis.from_url(settings.REDIS_URL)


@app.post("/wallet/create", response_model=schemas.WalletResponse)
def create_wallet(
    wallet: schemas.WalletCreate,
    db: Session = Depends(lambda: next(get_db_session(engine))),
):
    db_wallet = (
        db.query(models.Wallet).filter(models.Wallet.user_id == wallet.user_id).first()
    )
    if db_wallet:
        raise HTTPException(
            status_code=400, detail="Wallet already exists for this user"
        )

    new_wallet = models.Wallet(user_id=wallet.user_id, currency=wallet.currency)
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)

    logger.info(f"Wallet created for user: {wallet.user_id}")
    return new_wallet


@app.get("/wallet/{id}", response_model=schemas.WalletResponse)
def get_wallet(id: int, db: Session = Depends(lambda: next(get_db_session(engine)))):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@app.get("/wallet/user/{user_id}", response_model=schemas.WalletResponse)
def get_wallet_by_user(
    user_id: int, db: Session = Depends(lambda: next(get_db_session(engine)))
):
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@app.post("/wallet/freeze", response_model=schemas.WalletResponse)
def freeze_wallet(
    data: schemas.WalletUpdate,
    wallet_id: int,
    db: Session = Depends(lambda: next(get_db_session(engine))),
):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    wallet.is_frozen = data.is_frozen
    db.commit()
    db.refresh(wallet)

    if data.is_frozen:
        publish_event(
            "wallet.frozen", {"wallet_id": wallet.id, "user_id": wallet.user_id}
        )

    return wallet


#############
# Internal APIs for Transaction Service
#############


@app.post("/wallet/internal/update_balance")
def update_balance(
    wallet_id: int,
    amount: float,
    db: Session = Depends(lambda: next(get_db_session(engine))),
):
    # Simple atomic update using a lock or database transaction
    # We use Redis lock to ensure safety if multiple transactions hit same wallet
    lock_key = f"LOCK:wallet:{wallet_id}"
    with redis_client.lock(lock_key, timeout=5):
        wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        if wallet.is_frozen:
            raise HTTPException(status_code=400, detail="Wallet is frozen")

        if wallet.balance + amount < 0:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        wallet.balance += amount
        db.commit()
        db.refresh(wallet)
        return {"new_balance": wallet.balance}
