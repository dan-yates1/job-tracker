from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from ..core.security import create_access_token
from ..core.supabase import get_supabase, supabase_client
from ..schemas.user import UserCreate, User
from ..config import settings

def get_password_hash(password: str) -> str:
    # Generate a salt and hash the password
    salt = bcrypt.gensalt(rounds=12)
    password_bytes = password.encode()
    hash_bytes = bcrypt.hashpw(password_bytes, salt)
    return hash_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Convert strings to bytes for bcrypt
        password_bytes = plain_password.encode()
        hash_bytes = hashed_password.encode()
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False

def get_user_by_email(email: str):
    """Get a user by email using service role key."""
    admin_client = get_supabase(use_service_key=True)
    result = admin_client.table('users').select('*').eq('email', email).execute()
    users = result.data
    return users[0] if users else None

def create_user(user: UserCreate):
    """Create a new user using service role key."""
    admin_client = get_supabase(use_service_key=True)
    
    # Hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)
    
    # Prepare user data
    user_data = {
        'email': user.email,
        'password': hashed_password.decode('utf-8'),
        'full_name': user.full_name,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    # Insert the user
    result = admin_client.table('users').insert(user_data).execute()
    return result.data[0]

def authenticate_user(email: str, password: str):
    """Authenticate a user."""
    user = get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
