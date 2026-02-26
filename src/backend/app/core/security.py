from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from .config import settings
import hashlib

# Password hashing context using argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain text password"""
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(password, hashed)


def create_token(sub: str, role_name: str, token_version: int):
    """
    Create JWT token.
    `sub` is typically the user's email.
    `role_name` is included for quick role checks in the token payload.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": sub,
        "exp": expire,
        "role": role_name,
        "token_version": token_version,
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> dict | None:
    """
    Decode and validate JWT.
    Returns payload if valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("sub") is None:
            return None

        return payload

    except JWTError:
        return None
    
def create_refresh_token(sub: str):
    expire = datetime.now(timezone.utc) + timedelta(days=7)

    payload = {
        "sub": sub,
        "exp": expire,
        "type": "refresh"
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()