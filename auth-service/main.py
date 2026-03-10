import models
import schemas
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from shared.config import settings
from shared.database import Base, get_db_engine, get_db_session
from shared.logging_utils import get_logger
from shared.messaging import publish_event
from shared.security import create_access_token, get_password_hash, verify_password

logger = get_logger("auth-service")

app = FastAPI()

# Database Setup
engine = get_db_engine(settings.DATABASE_URL)
models.Base.metadata.create_all(bind=engine)


@app.post("/auth/register", response_model=schemas.UserResponse)
def register(
    user: schemas.UserCreate,
    db: Session = Depends(lambda: next(get_db_session(engine))),
):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        name=user.name,
        phone=user.phone,
        password_hash=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"User registered: {new_user.id}")

    # Publish Event
    publish_event(
        "user.registered",
        {"user_id": new_user.id, "email": new_user.email, "name": new_user.name},
    )

    return new_user


@app.post("/auth/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(lambda: next(get_db_session(engine))),
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=schemas.UserResponse)
def read_users_me(
    token: str, db: Session = Depends(lambda: next(get_db_session(engine)))
):
    # In a real microservice, Gateway handles auth mostly, but internal check is good.
    # Here we just decode token for demo or assume gateway passes user info.
    # For simplicity, we'll implement full check or trust headers?
    # Let's decode token.
    from shared.security import decode_access_token

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
