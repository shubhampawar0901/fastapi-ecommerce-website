"""
Users router for user profile management
Handles user profile operations and account management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from database import get_db
from models.user import User
from schemas import UserUpdate, UserResponse, MessageResponse
from auth import get_current_user, get_password_hash

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile information
    """
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile information
    """
    try:
        # Update user fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"User profile updated: {current_user.email}")
        return current_user
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change user's password
    """
    try:
        from auth import verify_password
        
        # Verify current password
        if not verify_password(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long"
            )
        
        # Update password
        current_user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        return {"message": "Password changed successfully", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.delete("/account", response_model=MessageResponse)
async def delete_user_account(
    password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete user account (requires password confirmation)
    """
    try:
        from auth import verify_password
        
        # Verify password
        if not verify_password(password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect"
            )
        
        # Deactivate account instead of deleting (for data integrity)
        current_user.is_active = False
        db.commit()
        
        logger.info(f"User account deactivated: {current_user.email}")
        return {"message": "Account deactivated successfully", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account deletion error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )
