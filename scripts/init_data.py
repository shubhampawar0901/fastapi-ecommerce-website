"""
Sample data initialization script
Creates initial data for testing and demonstration
"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.product import Product, Category
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_data():
    """Create sample data for the e-commerce application"""
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            logger.info("Sample data already exists, skipping initialization")
            return
        
        logger.info("Creating sample data...")
        
        # Create admin user
        admin_user = User(
            email="admin@ecommerce.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        
        # Create sample customer
        customer_user = User(
            email="customer@example.com",
            username="customer",
            hashed_password=get_password_hash("customer123"),
            first_name="John",
            last_name="Doe",
            phone="+1234567890",
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=True,
            address_line1="123 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
            country="USA"
        )
        db.add(customer_user)
        
        # Create categories
        categories = [
            Category(
                name="Electronics",
                description="Electronic devices and gadgets",
                slug="electronics",
                is_active=True,
                sort_order=1
            ),
            Category(
                name="Clothing",
                description="Fashion and apparel",
                slug="clothing",
                is_active=True,
                sort_order=2
            ),
            Category(
                name="Books",
                description="Books and literature",
                slug="books",
                is_active=True,
                sort_order=3
            ),
            Category(
                name="Home & Garden",
                description="Home improvement and garden supplies",
                slug="home-garden",
                is_active=True,
                sort_order=4
            )
        ]
        
        for category in categories:
            db.add(category)
        
        db.flush()  # Get category IDs
        
        # Create sample products
        products = [
            # Electronics
            Product(
                name="Smartphone Pro Max",
                description="Latest flagship smartphone with advanced features",
                short_description="Premium smartphone with excellent camera",
                sku="PHONE-001",
                slug="smartphone-pro-max",
                price=999.99,
                compare_price=1199.99,
                stock_quantity=50,
                category_id=categories[0].id,
                is_active=True,
                is_featured=True,
                brand="TechBrand",
                color="Black",
                weight=0.2,
                dimensions="6.1 x 3.0 x 0.3 inches",
                image_url="https://example.com/images/smartphone.jpg",
                tags="smartphone,mobile,electronics,featured"
            ),
            Product(
                name="Wireless Headphones",
                description="Premium noise-cancelling wireless headphones",
                short_description="High-quality wireless headphones",
                sku="HEAD-001",
                slug="wireless-headphones",
                price=299.99,
                stock_quantity=30,
                category_id=categories[0].id,
                is_active=True,
                brand="AudioTech",
                color="White",
                weight=0.3,
                image_url="https://example.com/images/headphones.jpg",
                tags="headphones,audio,wireless,electronics"
            ),
            
            # Clothing
            Product(
                name="Classic T-Shirt",
                description="Comfortable cotton t-shirt for everyday wear",
                short_description="100% cotton classic fit t-shirt",
                sku="SHIRT-001",
                slug="classic-t-shirt",
                price=24.99,
                stock_quantity=100,
                category_id=categories[1].id,
                is_active=True,
                brand="FashionCo",
                color="Blue",
                size="M",
                image_url="https://example.com/images/tshirt.jpg",
                tags="clothing,shirt,cotton,casual"
            ),
            Product(
                name="Denim Jeans",
                description="Premium denim jeans with modern fit",
                short_description="Stylish and comfortable denim jeans",
                sku="JEANS-001",
                slug="denim-jeans",
                price=79.99,
                compare_price=99.99,
                stock_quantity=75,
                category_id=categories[1].id,
                is_active=True,
                brand="DenimWorks",
                color="Dark Blue",
                size="32",
                image_url="https://example.com/images/jeans.jpg",
                tags="clothing,jeans,denim,pants"
            ),
            
            # Books
            Product(
                name="Python Programming Guide",
                description="Comprehensive guide to Python programming",
                short_description="Learn Python programming from basics to advanced",
                sku="BOOK-001",
                slug="python-programming-guide",
                price=39.99,
                stock_quantity=25,
                category_id=categories[2].id,
                is_active=True,
                is_digital=True,
                brand="TechBooks",
                image_url="https://example.com/images/python-book.jpg",
                tags="books,programming,python,education"
            ),
            
            # Home & Garden
            Product(
                name="Indoor Plant Pot",
                description="Decorative ceramic pot for indoor plants",
                short_description="Beautiful ceramic pot for your plants",
                sku="POT-001",
                slug="indoor-plant-pot",
                price=19.99,
                stock_quantity=40,
                category_id=categories[3].id,
                is_active=True,
                color="White",
                weight=1.5,
                dimensions="8 x 8 x 10 inches",
                image_url="https://example.com/images/plant-pot.jpg",
                tags="home,garden,plants,decoration"
            )
        ]
        
        for product in products:
            db.add(product)
        
        db.commit()
        logger.info("Sample data created successfully!")
        
        # Print summary
        logger.info(f"Created {len(categories)} categories")
        logger.info(f"Created {len(products)} products")
        logger.info("Created 1 admin user (admin@ecommerce.com / admin123)")
        logger.info("Created 1 customer user (customer@example.com / customer123)")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
