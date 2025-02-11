from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from ..core.security import verify_password, get_password_hash, create_tokens
from ..core.supabase import get_supabase
from ..schemas.user import UserCreate, UserUpdate, User, UserInDB
from ..models.user import UserRole

class UserService:
    def __init__(self):
        self.client = get_supabase()

    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get a user by email."""
        result = self.client.table('users').select('*').eq('email', email).execute()
        users = result.data
        return UserInDB(**users[0]) if users else None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        result = self.client.table('users').select('*').eq('id', user_id).execute()
        users = result.data
        return User(**users[0]) if users else None

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user exists
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Prepare user data
        user_dict = user_data.model_dump()
        user_dict.pop('password')  # Remove plain password
        user_dict.update({
            'hashed_password': hashed_password,
            'role': UserRole.USER,
            'is_active': True,
            'is_verified': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        # Create user
        result = self.client.table('users').insert(user_dict).execute()
        return User(**result.data[0])

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate a user and return tokens."""
        user = self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Update last login
        self.client.table('users').update({
            'last_login': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }).eq('id', user.id).execute()
        
        # Create tokens
        return self.create_tokens(user)

    def update_user(self, user_id: str, update_data: UserUpdate) -> User:
        """Update user information."""
        # Check if user exists
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare update data
        update_dict = update_data.model_dump(exclude_unset=True)
        update_dict['updated_at'] = datetime.utcnow()
        
        # Update user
        result = self.client.table('users').update(update_dict).eq('id', user_id).execute()
        return User(**result.data[0])

    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password."""
        # Get user
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            return False
        
        # Hash new password
        hashed_password = get_password_hash(new_password)
        
        # Update password
        self.client.table('users').update({
            'hashed_password': hashed_password,
            'updated_at': datetime.utcnow()
        }).eq('id', user_id).execute()
        return True

    def create_tokens(self, user: UserInDB) -> Dict[str, Any]:
        """Create new access and refresh tokens for user."""
        access_token, refresh_token = create_tokens(user.email, user.role)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": User(**user.model_dump())
        }

    def list_users(self) -> List[User]:
        """List all users."""
        result = self.client.table('users').select('*').execute()
        return [User(**user) for user in result.data]


# Initialize user service
user_service = UserService()
