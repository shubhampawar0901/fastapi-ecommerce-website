"""
Admin router for administrative operations
Handles admin-only endpoints for system management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging

from app.core.database import get_db, get_db_info
from app.models.user import User, UserRole
from app.models.product import Product, Category
from app.models.order import Order, OrderStatus
from app.models.cart import Cart
from app.schemas import UserResponse, MessageResponse
from app.core.security import get_admin_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard")
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get admin dashboard statistics
    """
    try:
        # Get various statistics
        total_users = db.query(func.count(User.id)).scalar()
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
        total_products = db.query(func.count(Product.id)).scalar()
        active_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
        total_orders = db.query(func.count(Order.id)).scalar()
        pending_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.PENDING).scalar()
        total_categories = db.query(func.count(Category.id)).scalar()
        active_carts = db.query(func.count(Cart.id)).filter(Cart.status == "active").scalar()
        
        # Get recent orders
        recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
        
        # Get low stock products
        low_stock_products = db.query(Product).filter(
            Product.track_inventory == True,
            Product.stock_quantity <= Product.low_stock_threshold,
            Product.is_active == True
        ).limit(10).all()
        
        # Calculate total revenue (from completed orders)
        total_revenue = db.query(func.sum(Order.total_amount)).filter(
            Order.status.in_([OrderStatus.DELIVERED, OrderStatus.SHIPPED])
        ).scalar() or 0
        
        return {
            "statistics": {
                "total_users": total_users,
                "active_users": active_users,
                "total_products": total_products,
                "active_products": active_products,
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "total_categories": total_categories,
                "active_carts": active_carts,
                "total_revenue": float(total_revenue)
            },
            "recent_orders": [order.to_dict() for order in recent_orders],
            "low_stock_products": [product.to_dict() for product in low_stock_products],
            "database_info": get_db_info()
        }
        
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data"
        )

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of users to return"),
    role_filter: Optional[UserRole] = Query(None, description="Filter by user role"),
    active_only: bool = Query(False, description="Filter active users only"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get all users (Admin only)
    """
    try:
        query = db.query(User)
        
        if role_filter:
            query = query.filter(User.role == role_filter)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        return users
        
    except Exception as e:
        logger.error(f"Get all users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get specific user by ID (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Update user role (Admin only)
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent changing own role
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role"
            )
        
        user.role = new_role
        db.commit()
        db.refresh(user)
        
        logger.info(f"User role updated: {user.email} to {new_role.value} by {current_user.email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User role update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User role update failed"
        )

@router.put("/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Update user active status (Admin only)
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deactivating own account
        if user.id == current_user.id and not is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
        
        user.is_active = is_active
        db.commit()
        db.refresh(user)
        
        status_text = "activated" if is_active else "deactivated"
        logger.info(f"User {status_text}: {user.email} by {current_user.email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User status update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User status update failed"
        )

@router.get("/system/health")
async def system_health_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    System health check (Admin only)
    """
    try:
        # Test database connection
        db_info = get_db_info()
        
        # Get system statistics
        total_users = db.query(func.count(User.id)).scalar()
        total_products = db.query(func.count(Product.id)).scalar()
        total_orders = db.query(func.count(Order.id)).scalar()
        
        return {
            "status": "healthy",
            "database": db_info,
            "statistics": {
                "total_users": total_users,
                "total_products": total_products,
                "total_orders": total_orders
            },
            "timestamp": "2025-07-13T06:57:00Z"
        }
        
    except Exception as e:
        logger.error(f"System health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System health check failed"
        )

@router.post("/system/cleanup", response_model=MessageResponse)
async def cleanup_system(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Cleanup system data (Admin only)
    Removes abandoned carts and expired sessions
    """
    try:
        from datetime import datetime, timedelta
        
        # Remove abandoned carts older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        abandoned_carts = db.query(Cart).filter(
            Cart.status == "active",
            Cart.updated_at < cutoff_date
        ).count()
        
        db.query(Cart).filter(
            Cart.status == "active",
            Cart.updated_at < cutoff_date
        ).update({"status": "abandoned"})
        
        db.commit()
        
        logger.info(f"System cleanup completed: {abandoned_carts} carts marked as abandoned by {current_user.email}")
        return {
            "message": f"System cleanup completed. {abandoned_carts} abandoned carts processed.",
            "success": True
        }
        
    except Exception as e:
        logger.error(f"System cleanup error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System cleanup failed"
        )
