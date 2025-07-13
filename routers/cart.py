"""
Shopping cart router for cart management
Handles cart operations like add, update, remove items
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session, joinedload
from typing import Optional
import logging
import uuid

from database import get_db
from models.cart import Cart, CartItem
from models.product import Product
from models.user import User
from schemas import CartItemCreate, CartItemUpdate, CartResponse, MessageResponse
from auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

def get_or_create_cart(db: Session, user: Optional[User] = None, session_id: Optional[str] = None) -> Cart:
    """
    Get existing cart or create new one for user or session
    """
    if user:
        # Get user's active cart
        cart = db.query(Cart).filter(
            Cart.user_id == user.id,
            Cart.status == "active"
        ).first()
        
        if not cart:
            cart = Cart(user_id=user.id, status="active")
            db.add(cart)
            db.commit()
            db.refresh(cart)
    else:
        # Get or create guest cart by session
        if not session_id:
            session_id = str(uuid.uuid4())
        
        cart = db.query(Cart).filter(
            Cart.session_id == session_id,
            Cart.status == "active"
        ).first()
        
        if not cart:
            cart = Cart(session_id=session_id, status="active")
            db.add(cart)
            db.commit()
            db.refresh(cart)
    
    return cart

@router.get("/", response_model=CartResponse)
async def get_cart(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Get current user's cart or guest cart
    """
    try:
        cart = get_or_create_cart(db, current_user, session_id)
        
        # Load cart with items and products
        cart_with_items = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.id == cart.id).first()
        
        return cart_with_items
        
    except Exception as e:
        logger.error(f"Get cart error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cart"
        )

@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Add item to cart or update quantity if item already exists
    """
    try:
        # Get or create cart
        cart = get_or_create_cart(db, current_user, session_id)
        
        # Validate product exists and is active
        product = db.query(Product).filter(
            Product.id == item_data.product_id,
            Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or inactive"
            )
        
        # Check stock availability
        if product.track_inventory and not product.allow_backorder:
            if product.stock_quantity < item_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock. Available: {product.stock_quantity}"
                )
        
        # Check if item already exists in cart
        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item_data.product_id,
            CartItem.product_options == item_data.product_options
        ).first()
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + item_data.quantity
            
            # Check stock for new quantity
            if product.track_inventory and not product.allow_backorder:
                if product.stock_quantity < new_quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock. Available: {product.stock_quantity}, Requested: {new_quantity}"
                    )
            
            existing_item.quantity = new_quantity
        else:
            # Create new cart item
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=product.price,
                product_options=item_data.product_options
            )
            db.add(cart_item)
        
        db.commit()
        
        # Return updated cart
        cart_with_items = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.id == cart.id).first()
        
        logger.info(f"Item added to cart: Product {item_data.product_id}, Quantity {item_data.quantity}")
        return cart_with_items
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add to cart error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        )

@router.put("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Update cart item quantity
    """
    try:
        # Get cart
        cart = get_or_create_cart(db, current_user, session_id)
        
        # Get cart item
        cart_item = db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        ).first()
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        
        # Validate product stock
        product = cart_item.product
        if product.track_inventory and not product.allow_backorder:
            if product.stock_quantity < item_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock. Available: {product.stock_quantity}"
                )
        
        # Update quantity
        cart_item.quantity = item_data.quantity
        db.commit()
        
        # Return updated cart
        cart_with_items = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.id == cart.id).first()
        
        logger.info(f"Cart item updated: Item {item_id}, New quantity {item_data.quantity}")
        return cart_with_items
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update cart item error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cart item"
        )

@router.delete("/items/{item_id}", response_model=MessageResponse)
async def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Remove item from cart
    """
    try:
        # Get cart
        cart = get_or_create_cart(db, current_user, session_id)
        
        # Get cart item
        cart_item = db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        ).first()
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        
        db.delete(cart_item)
        db.commit()
        
        logger.info(f"Cart item removed: Item {item_id}")
        return {"message": "Item removed from cart", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove cart item error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove cart item"
        )

@router.delete("/clear", response_model=MessageResponse)
async def clear_cart(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Clear all items from cart
    """
    try:
        # Get cart
        cart = get_or_create_cart(db, current_user, session_id)
        
        # Delete all cart items
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()
        
        logger.info(f"Cart cleared: Cart {cart.id}")
        return {"message": "Cart cleared successfully", "success": True}
        
    except Exception as e:
        logger.error(f"Clear cart error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cart"
        )
