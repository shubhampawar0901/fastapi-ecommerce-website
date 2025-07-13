"""
Shopping cart models for e-commerce functionality
Handles cart sessions and cart items for users
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Cart(Base):
    """
    Shopping cart model for user sessions
    Stores cart information and manages cart lifecycle
    """
    __tablename__ = "carts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User relationship (nullable for guest carts)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Session management for guest users
    session_id = Column(String(255), nullable=True, index=True)
    
    # Cart status and metadata
    status = Column(String(20), default="active")  # active, abandoned, converted
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, items_count={len(self.items)})>"
    
    @property
    def total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items)
    
    @property
    def total_amount(self):
        """Calculate total cart amount"""
        return sum(item.subtotal for item in self.items)
    
    @property
    def is_empty(self):
        """Check if cart is empty"""
        return len(self.items) == 0
    
    def to_dict(self):
        """Convert cart object to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "status": self.status,
            "total_items": self.total_items,
            "total_amount": float(self.total_amount),
            "is_empty": self.is_empty,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "items": [item.to_dict() for item in self.items]
        }

class CartItem(Base):
    """
    Cart item model for individual products in cart
    Links products to carts with quantity and pricing
    """
    __tablename__ = "cart_items"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item details
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)  # Price at time of adding to cart
    
    # Product options (for variants like size, color)
    product_options = Column(String(500), nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('cart_id', 'product_id', 'product_options', name='unique_cart_product_options'),
    )
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, cart_id={self.cart_id}, product_id={self.product_id}, quantity={self.quantity})>"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.quantity * self.unit_price
    
    def to_dict(self):
        """Convert cart item object to dictionary"""
        return {
            "id": self.id,
            "cart_id": self.cart_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "subtotal": float(self.subtotal),
            "product_options": self.product_options,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "product": self.product.to_dict() if self.product else None
        }
