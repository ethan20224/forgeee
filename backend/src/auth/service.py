import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from src.config import get_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: uuid.UUID) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: uuid.UUID) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: str = "access") -> uuid.UUID:
    """Decode and validate a JWT token. Returns the user_id.

    Raises:
        JWTError: If the token is invalid, expired, or wrong type.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise

    token_type = payload.get("type")
    if token_type != expected_type:
        raise JWTError(f"Expected {expected_type} token, got {token_type}")

    sub = payload.get("sub")
    if sub is None:
        raise JWTError("Token missing subject")

    return uuid.UUID(sub)
