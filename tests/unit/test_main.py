"""
Basic tests for the FastAPI e-commerce application
Tests core functionality and API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Clean up
    Base.metadata.drop_all(bind=engine)

def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "FastAPI E-commerce API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "healthy"

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["database"] == "connected"

def test_user_registration(client):
    """Test user registration"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data

def test_user_login(client):
    """Test user login"""
    # First register a user
    user_data = {
        "email": "login@example.com",
        "username": "loginuser",
        "password": "loginpassword123"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Then login
    login_data = {
        "email": "login@example.com",
        "password": "loginpassword123"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data

def test_get_products_empty(client):
    """Test getting products when none exist"""
    response = client.get("/api/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_categories_empty(client):
    """Test getting categories when none exist"""
    response = client.get("/api/products/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_cart_without_auth(client):
    """Test getting cart without authentication"""
    response = client.get("/api/cart/")
    assert response.status_code == 403

def test_protected_endpoint_without_auth(client):
    """Test accessing protected endpoint without authentication"""
    response = client.get("/api/auth/me")
    assert response.status_code == 403

def test_admin_endpoint_without_auth(client):
    """Test accessing admin endpoint without authentication"""
    response = client.get("/api/admin/dashboard")
    assert response.status_code == 403

def test_invalid_login(client):
    """Test login with invalid credentials"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401

def test_duplicate_user_registration(client):
    """Test registering user with duplicate email"""
    user_data = {
        "email": "duplicate@example.com",
        "username": "duplicate1",
        "password": "password123"
    }
    # First registration should succeed
    response1 = client.post("/api/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Second registration with same email should fail
    user_data["username"] = "duplicate2"
    response2 = client.post("/api/auth/register", json=user_data)
    assert response2.status_code == 400

def test_api_documentation(client):
    """Test that API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200

def test_user_authentication_flow(client):
    """Test complete user authentication flow"""
    # Register user
    user_data = {
        "email": "flow@example.com",
        "username": "flowuser",
        "password": "flowpassword123",
        "first_name": "Flow",
        "last_name": "User"
    }
    register_response = client.post("/api/auth/register", json=user_data)
    assert register_response.status_code == 201

    # Login user
    login_data = {
        "email": "flow@example.com",
        "password": "flowpassword123"
    }
    login_response = client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200

    token_data = login_response.json()
    access_token = token_data["access_token"]

    # Access protected endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200

    user_info = me_response.json()
    assert user_info["email"] == "flow@example.com"
    assert user_info["username"] == "flowuser"

def test_product_management_flow(client):
    """Test product management flow"""
    # Get products (should be empty initially)
    response = client.get("/api/products/")
    assert response.status_code == 200
    products = response.json()
    assert isinstance(products, list)

    # Get categories (should be empty initially)
    response = client.get("/api/products/categories")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)

def test_cart_operations_without_auth(client):
    """Test cart operations without authentication"""
    # Try to get cart without auth - should fail
    response = client.get("/api/cart/")
    assert response.status_code == 403

    # Try to add item without auth - should fail
    item_data = {"product_id": 1, "quantity": 1}
    response = client.post("/api/cart/items", json=item_data)
    assert response.status_code == 403

def test_admin_endpoints_without_auth(client):
    """Test admin endpoints without authentication"""
    response = client.get("/api/admin/dashboard")
    assert response.status_code == 403

    response = client.get("/api/admin/users")
    assert response.status_code == 403

def test_error_handling(client):
    """Test error handling for various scenarios"""
    # Test 404 for non-existent product
    response = client.get("/api/products/99999")
    assert response.status_code == 404

    # Test validation error for invalid registration data
    invalid_user_data = {
        "email": "invalid-email",
        "username": "a",  # Too short
        "password": "123"  # Too short
    }
    response = client.post("/api/auth/register", json=invalid_user_data)
    assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__])
