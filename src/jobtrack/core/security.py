from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import bcrypt
from jose import JWTError, jwt

from .config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_tokens(email: str, role: str) -> Tuple[str, str]:
    """Create access and refresh tokens."""
    # Access token with shorter expiry
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_token(
        data={"sub": email, "role": role, "type": "access"},
        expires_delta=access_token_expires
    )
    
    # Refresh token with longer expiry
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
    refresh_token = create_token(
        data={"sub": email, "role": role, "type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    return access_token, refresh_token

def create_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[Dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None
