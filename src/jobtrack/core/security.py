from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from uuid import uuid4

from ..config import settings
from ..models.user import UserRole

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_tokens(email: str, role: UserRole) -> Tuple[str, str]:
    """Create access and refresh tokens."""
    # Access token - short lived
    access_token_data = {
        "sub": email,
        "role": role,
        "type": "access",
        "jti": str(uuid4())
    }
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(access_token_data, access_token_expires)

    # Refresh token - long lived
    refresh_token_data = {
        "sub": email,
        "role": role,
        "type": "refresh",
        "jti": str(uuid4())
    }
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_jwt_token(refresh_token_data, refresh_token_expires)

    return access_token, refresh_token

def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    """Create a JWT token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Verify token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type} token."
            )
        
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def get_token_data(token: str, token_type: str = "access") -> dict:
    """Get token data and validate token type."""
    payload = verify_token(token, token_type)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return {
        "email": payload.get("sub"),
        "role": payload.get("role")
    }
