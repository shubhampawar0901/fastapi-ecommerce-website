"""
Products router for product catalog management
Handles product CRUD operations and product search
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models.product import Product, Category
from app.models.user import User
from app.schemas import (
    ProductCreate, ProductUpdate, ProductResponse, CategoryCreate,
    CategoryUpdate, CategoryResponse, PaginatedResponse
)
from app.core.security import get_current_user, get_admin_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Category endpoints
@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Create a new product category (Admin only)
    """
    try:
        # Check if category with same slug exists
        existing_category = db.query(Category).filter(Category.slug == category_data.slug).first()
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this slug already exists"
            )
        
        # Validate parent category if specified
        if category_data.parent_id:
            parent_category = db.query(Category).filter(Category.id == category_data.parent_id).first()
            if not parent_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent category not found"
                )
        
        db_category = Category(**category_data.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        logger.info(f"Category created: {db_category.name} by {current_user.email}")
        return db_category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Category creation error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Category creation failed"
        )

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    active_only: bool = Query(True, description="Filter active categories only"),
    db: Session = Depends(get_db)
):
    """
    Get all product categories
    """
    try:
        query = db.query(Category)
        if active_only:
            query = query.filter(Category.is_active == True)
        
        categories = query.order_by(Category.sort_order, Category.name).all()
        return categories
        
    except Exception as e:
        logger.error(f"Get categories error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve categories"
        )

@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Get a specific category by ID
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

# Product endpoints
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Create a new product (Admin only)
    """
    try:
        # Check if product with same SKU exists
        existing_product = db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists"
            )
        
        # Check if product with same slug exists
        existing_slug = db.query(Product).filter(Product.slug == product_data.slug).first()
        if existing_slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this slug already exists"
            )
        
        # Validate category if specified
        if product_data.category_id:
            category = db.query(Category).filter(Category.id == product_data.category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found"
                )
        
        db_product = Product(**product_data.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        logger.info(f"Product created: {db_product.name} by {current_user.email}")
        return db_product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Product creation error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Product creation failed"
        )

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of products to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search in product name and description"),
    active_only: bool = Query(True, description="Filter active products only"),
    featured_only: bool = Query(False, description="Filter featured products only"),
    in_stock_only: bool = Query(False, description="Filter products in stock only"),
    db: Session = Depends(get_db)
):
    """
    Get products with filtering and pagination
    """
    try:
        query = db.query(Product).options(joinedload(Product.category))
        
        # Apply filters
        if active_only:
            query = query.filter(Product.is_active == True)
        
        if featured_only:
            query = query.filter(Product.is_featured == True)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if in_stock_only:
            query = query.filter(
                or_(
                    Product.track_inventory == False,
                    and_(Product.track_inventory == True, Product.stock_quantity > 0),
                    and_(Product.track_inventory == True, Product.allow_backorder == True)
                )
            )
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.short_description.ilike(search_term),
                    Product.tags.ilike(search_term)
                )
            )
        
        # Apply pagination
        products = query.offset(skip).limit(limit).all()
        return products
        
    except Exception as e:
        logger.error(f"Get products error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products"
        )

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product by ID
    """
    product = db.query(Product).options(joinedload(Product.category)).filter(
        Product.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product

@router.get("/slug/{product_slug}", response_model=ProductResponse)
async def get_product_by_slug(product_slug: str, db: Session = Depends(get_db)):
    """
    Get a specific product by slug
    """
    product = db.query(Product).options(joinedload(Product.category)).filter(
        Product.slug == product_slug
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Update a product (Admin only)
    """
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Update product fields
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        
        logger.info(f"Product updated: {product.name} by {current_user.email}")
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Product update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Product update failed"
        )

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Delete a product (Admin only)
    """
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        db.delete(product)
        db.commit()
        
        logger.info(f"Product deleted: {product.name} by {current_user.email}")
        return {"message": "Product deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Product deletion error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Product deletion failed"
        )
