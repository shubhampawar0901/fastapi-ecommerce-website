"""
Product and Category models for e-commerce catalog
Handles product information, categories, and inventory
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql.sqltypes import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Category(Base):
    """
    Product category model for organizing products
    Supports hierarchical categories with parent-child relationships
    """
    __tablename__ = "categories"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Category information
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    
    # Hierarchy support
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Display and status
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    # SEO and metadata
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"

class Product(Base):
    """
    Product model for e-commerce items
    Stores product information, pricing, and inventory
    """
    __tablename__ = "products"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic product information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    
    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    compare_price = Column(Numeric(10, 2), nullable=True)  # Original price for discounts
    cost_price = Column(Numeric(10, 2), nullable=True)     # Cost for profit calculation
    
    # Inventory management
    stock_quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    track_inventory = Column(Boolean, default=True)
    allow_backorder = Column(Boolean, default=False)
    
    # Product attributes
    weight = Column(Numeric(8, 2), nullable=True)
    dimensions = Column(String(100), nullable=True)  # Format: "L x W x H"
    color = Column(String(50), nullable=True)
    size = Column(String(50), nullable=True)
    brand = Column(String(100), nullable=True)
    
    # Images and media
    image_url = Column(String(500), nullable=True)
    gallery_images = Column(Text, nullable=True)  # JSON string of image URLs
    
    # Category relationship
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Status and visibility
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_digital = Column(Boolean, default=False)
    
    # SEO and metadata
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0 or self.allow_backorder
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock"""
        if not self.track_inventory:
            return False
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare_price is set"""
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100, 2)
        return 0
    
    def to_dict(self):
        """Convert product object to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "short_description": self.short_description,
            "sku": self.sku,
            "slug": self.slug,
            "price": float(self.price),
            "compare_price": float(self.compare_price) if self.compare_price else None,
            "stock_quantity": self.stock_quantity,
            "is_in_stock": self.is_in_stock,
            "is_low_stock": self.is_low_stock,
            "weight": float(self.weight) if self.weight else None,
            "dimensions": self.dimensions,
            "color": self.color,
            "size": self.size,
            "brand": self.brand,
            "image_url": self.image_url,
            "category_id": self.category_id,
            "is_active": self.is_active,
            "is_featured": self.is_featured,
            "is_digital": self.is_digital,
            "tags": self.tags.split(",") if self.tags else [],
            "discount_percentage": self.discount_percentage,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
