from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth.database import SessionLocal
from auth.models import User
 
 
from .jwt_utils import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
 
from redis_client import redis_client
 
router = APIRouter()
 
# Token URL for Swagger OAuth2
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme = APIKeyHeader(
    name="Authorization",
    description="Enter token like: Bearer <your_jwt_token>"
)
 
# # Temporary DB
# fake_users_db = {}
 
 
# -----------------------------
# Pydantic Models
# -----------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
class RegisterModel(BaseModel):
    username: str
    password: str
 
class LoginModel(BaseModel):
    username: str
    password: str
 
 
# -----------------------------
# Register user
# -----------------------------
@router.post("/register")
def register(data: RegisterModel, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
 
    hashed_pass = hash_password(data.password)
    new_user = User(username=data.username, password=hashed_pass)
 
    db.add(new_user)
    db.commit()
 
    return {"message": "User registered"}
 
 
# -----------------------------
# Login user (returns JWT)
# -----------------------------
@router.post("/login")
def login(data: LoginModel, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
 
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
 
    token = create_access_token({"sub": data.username})
    return {"access_token": token, "token_type": "bearer"}
 
 
# -----------------------------
# Get current user (token check)
# -----------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "").strip()
    
    payload = decode_access_token(token)
    print(f"TOKEN : {token}")
    print(f"payload : {payload}")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
 
    username = payload.get("sub")
 
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
 
    # blacklist check
    if redis_client.sismember("jwt_blacklist", token):
        raise HTTPException(status_code=401, detail="Token blocked")
 
    return username
 
 
# -----------------------------
# Logout user (blacklist JWT)
# -----------------------------
@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    redis_client.sadd("jwt_blacklist", token)
    return {"message": "Logged out"}
 