from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from redis_client import redis_client
 
SECRET_KEY = "033732c1a7774cae57840eb85c4af013f6119e25aa5d425a90ae98b8683952fd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 360
 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
 
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
 
 
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)
 
 
def create_access_token(data: dict, expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_in)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token
 
 
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
 