from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any

from ..services.user import user_service
from ..schemas.user import (
    User,
    UserCreate,
    UserUpdate,
    Token,
    PasswordReset,
    PasswordChange
)
from ..core.auth import (
    get_current_user,
    get_current_admin_user,
    check_permissions
)
from ..models.user import UserRole
from ..core.security import verify_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User)
async def register(user_data: UserCreate) -> Any:
    """Register a new user."""
    return user_service.create_user(user_data)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """Login and get access token."""
    auth_result = user_service.authenticate_user(form_data.username, form_data.password)
    return {
        "access_token": auth_result["access_token"],
        "refresh_token": auth_result["refresh_token"],
        "token_type": auth_result["token_type"]
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str) -> Any:
    """Get new access token using refresh token."""
    # Verify refresh token
    token_data = verify_token(refresh_token, token_type="refresh")
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user and create new tokens
    user = user_service.get_user_by_email(token_data["email"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    auth_result = user_service.create_tokens(user)
    return {
        "access_token": auth_result["access_token"],
        "refresh_token": auth_result["refresh_token"],
        "token_type": auth_result["token_type"]
    }

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    """Get current user information."""
    return current_user

@router.patch("/me", response_model=User)
async def update_user_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update current user information."""
    return user_service.update_user(current_user.id, update_data)

@router.post("/password/change")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Change user password."""
    if user_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    ):
        return {"message": "Password changed successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Password change failed"
    )

@router.post("/password/reset")
async def request_password_reset(email_data: PasswordReset) -> Any:
    """Request password reset."""
    # This would typically send a password reset email
    # For now, we'll just return a success message
    user = user_service.get_user_by_email(email_data.email)
    if user:
        # TODO: Implement email sending
        return {"message": "If the email exists, a password reset link will be sent"}
    return {"message": "If the email exists, a password reset link will be sent"}

# Admin routes
@router.get("/users", response_model=list[User])
async def list_users(
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """List all users (admin only)."""
    return user_service.list_users()

@router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """Get user by ID (admin only)."""
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.patch("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """Update user (admin only)."""
    return user_service.update_user(user_id, update_data)
