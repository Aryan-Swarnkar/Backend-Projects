from pwdlib import PasswordHash
from datetime import timedelta, timezone, datetime
import jwt
from app.core.config import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_hash.verify(password, hashed_pass)

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }
    
    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    