"""
Orders router for order management
Handles order creation, tracking, and order history
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import logging
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas import OrderCreate, OrderResponse, MessageResponse
from app.core.security import get_current_user, get_admin_user

logger = logging.getLogger(__name__)
router = APIRouter()

def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid.uuid4())[:8].upper()
    return f"ORD-{timestamp}-{random_suffix}"

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order from user's cart
    """
    try:
        # Get user's active cart
        cart = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(
            Cart.user_id == current_user.id,
            Cart.status == "active"
        ).first()
        
        if not cart or cart.is_empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )
        
        # Validate stock availability for all items
        for cart_item in cart.items:
            product = cart_item.product
            if product.track_inventory and not product.allow_backorder:
                if product.stock_quantity < cart_item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
                    )
        
        # Calculate order totals
        subtotal = cart.total_amount
        tax_amount = subtotal * 0.1  # 10% tax (configurable)
        shipping_amount = 10.00 if subtotal < 100 else 0  # Free shipping over $100
        total_amount = subtotal + tax_amount + shipping_amount
        
        # Create order
        order = Order(
            order_number=generate_order_number(),
            user_id=current_user.id,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_amount=shipping_amount,
            discount_amount=0,
            total_amount=total_amount,
            
            # Shipping address
            shipping_address_line1=order_data.shipping_address.line1,
            shipping_address_line2=order_data.shipping_address.line2,
            shipping_city=order_data.shipping_address.city,
            shipping_state=order_data.shipping_address.state,
            shipping_postal_code=order_data.shipping_address.postal_code,
            shipping_country=order_data.shipping_address.country,
            
            # Billing address
            billing_address_line1=order_data.billing_address.line1,
            billing_address_line2=order_data.billing_address.line2,
            billing_city=order_data.billing_address.city,
            billing_state=order_data.billing_address.state,
            billing_postal_code=order_data.billing_address.postal_code,
            billing_country=order_data.billing_address.country,
            
            # Customer information
            customer_name=order_data.customer_name,
            customer_email=order_data.customer_email,
            customer_phone=order_data.customer_phone,
            
            # Payment information
            payment_method=order_data.payment_method,
            notes=order_data.notes
        )
        
        db.add(order)
        db.flush()  # Get order ID
        
        # Create order items from cart items
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                product_options=cart_item.product_options
            )
            db.add(order_item)
            
            # Update product stock
            if cart_item.product.track_inventory:
                cart_item.product.stock_quantity -= cart_item.quantity
        
        # Mark cart as converted
        cart.status = "converted"
        
        db.commit()
        db.refresh(order)
        
        # Load order with items
        order_with_items = db.query(Order).options(
            joinedload(Order.items)
        ).filter(Order.id == order.id).first()
        
        logger.info(f"Order created: {order.order_number} for user {current_user.email}")
        return order_with_items
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Order creation error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Order creation failed"
        )

@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of orders to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's order history
    """
    try:
        orders = db.query(Order).options(
            joinedload(Order.items)
        ).filter(
            Order.user_id == current_user.id
        ).order_by(
            Order.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return orders
        
    except Exception as e:
        logger.error(f"Get user orders error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders"
        )

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific order details
    """
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order

@router.get("/number/{order_number}", response_model=OrderResponse)
async def get_order_by_number(
    order_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get order by order number
    """
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(
        Order.order_number == order_number,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order

@router.post("/{order_id}/cancel", response_model=MessageResponse)
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an order (only if not shipped)
    """
    try:
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check if order can be cancelled
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order cannot be cancelled"
            )
        
        # Update order status
        order.status = OrderStatus.CANCELLED
        
        # Restore product stock
        for order_item in order.items:
            product = db.query(Product).filter(Product.id == order_item.product_id).first()
            if product and product.track_inventory:
                product.stock_quantity += order_item.quantity
        
        db.commit()
        
        logger.info(f"Order cancelled: {order.order_number} by user {current_user.email}")
        return {"message": "Order cancelled successfully", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Order cancellation error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Order cancellation failed"
        )

# Admin endpoints
@router.get("/admin/all", response_model=List[OrderResponse])
async def get_all_orders(
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of orders to return"),
    status_filter: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get all orders (Admin only)
    """
    try:
        query = db.query(Order).options(joinedload(Order.items))
        
        if status_filter:
            query = query.filter(Order.status == status_filter)
        
        orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        return orders
        
    except Exception as e:
        logger.error(f"Get all orders error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders"
        )

@router.put("/admin/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    tracking_number: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Update order status (Admin only)
    """
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Update order status
        order.status = new_status
        
        if tracking_number:
            order.tracking_number = tracking_number
        
        # Update timestamps based on status
        if new_status == OrderStatus.SHIPPED:
            order.shipped_at = datetime.utcnow()
        elif new_status == OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()
        
        db.commit()
        db.refresh(order)
        
        logger.info(f"Order status updated: {order.order_number} to {new_status.value} by {current_user.email}")
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Order status update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Order status update failed"
        )
