# FastAPI E-commerce API Documentation

Complete API documentation for the FastAPI e-commerce application with examples and usage patterns.

## Base URL

- **Local Development**: `http://localhost:8000`
- **Production**: `https://your-app-name.onrender.com`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

## API Endpoints

### Health Check

#### GET /
Root endpoint with basic API information.

**Response:**
```json
{
  "message": "FastAPI E-commerce API",
  "version": "1.0.0",
  "status": "healthy",
  "docs": "/docs"
}
```

#### GET /health
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-13",
  "database": "connected"
}
```

### Authentication Endpoints

#### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "newuser",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "newuser",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "customer",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-07-13T07:00:00"
}
```

#### POST /api/auth/login
Authenticate user and get access tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "newuser",
    "role": "customer"
  }
}
```

#### POST /api/auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### GET /api/auth/me
Get current authenticated user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "newuser",
  "first_name": "John",
  "last_name": "Doe",
  "role": "customer",
  "is_active": true
}
```

### Product Endpoints

#### GET /api/products/
Get products with filtering and pagination.

**Query Parameters:**
- `skip`: Number of products to skip (default: 0)
- `limit`: Number of products to return (default: 20, max: 100)
- `category_id`: Filter by category ID
- `search`: Search in product name and description
- `active_only`: Filter active products only (default: true)
- `featured_only`: Filter featured products only (default: false)
- `in_stock_only`: Filter products in stock only (default: false)

**Example:**
```
GET /api/products/?search=smartphone&category_id=1&limit=10
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Smartphone Pro Max",
    "description": "Latest flagship smartphone",
    "sku": "PHONE-001",
    "slug": "smartphone-pro-max",
    "price": "999.99",
    "compare_price": "1199.99",
    "stock_quantity": 50,
    "is_in_stock": true,
    "is_featured": true,
    "brand": "TechBrand",
    "category": {
      "id": 1,
      "name": "Electronics",
      "slug": "electronics"
    }
  }
]
```

#### GET /api/products/{product_id}
Get specific product by ID.

#### GET /api/products/slug/{product_slug}
Get specific product by slug.

#### POST /api/products/ (Admin Only)
Create a new product.

**Headers:** `Authorization: Bearer <admin-token>`

**Request Body:**
```json
{
  "name": "New Product",
  "description": "Product description",
  "sku": "PROD-001",
  "slug": "new-product",
  "price": 99.99,
  "stock_quantity": 100,
  "category_id": 1,
  "is_active": true,
  "is_featured": false
}
```

### Category Endpoints

#### GET /api/products/categories
Get all product categories.

**Query Parameters:**
- `active_only`: Filter active categories only (default: true)

#### POST /api/products/categories (Admin Only)
Create a new category.

### Shopping Cart Endpoints

#### GET /api/cart/
Get current user's cart.

**Headers:** 
- `Authorization: Bearer <token>` (for authenticated users)
- `X-Session-ID: <session-id>` (for guest users)

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "total_items": 3,
  "total_amount": "149.97",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "quantity": 2,
      "unit_price": "24.99",
      "subtotal": "49.98",
      "product": {
        "id": 1,
        "name": "Classic T-Shirt",
        "price": "24.99"
      }
    }
  ]
}
```

#### POST /api/cart/items
Add item to cart.

**Request Body:**
```json
{
  "product_id": 1,
  "quantity": 2,
  "product_options": "{\"size\": \"M\", \"color\": \"Blue\"}"
}
```

#### PUT /api/cart/items/{item_id}
Update cart item quantity.

**Request Body:**
```json
{
  "quantity": 3
}
```

#### DELETE /api/cart/items/{item_id}
Remove item from cart.

#### DELETE /api/cart/clear
Clear all items from cart.

### Order Endpoints

#### GET /api/orders/
Get current user's order history.

**Query Parameters:**
- `skip`: Number of orders to skip
- `limit`: Number of orders to return

#### GET /api/orders/{order_id}
Get specific order details.

#### POST /api/orders/
Create a new order from cart.

**Request Body:**
```json
{
  "shipping_address": {
    "line1": "123 Main St",
    "line2": "Apt 4B",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA"
  },
  "billing_address": {
    "line1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA"
  },
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "payment_method": "credit_card",
  "notes": "Please deliver after 5 PM"
}
```

#### POST /api/orders/{order_id}/cancel
Cancel an order (only if not shipped).

### User Management Endpoints

#### GET /api/users/profile
Get current user's profile.

#### PUT /api/users/profile
Update current user's profile.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address_line1": "123 Main St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA"
}
```

#### POST /api/users/change-password
Change user's password.

**Request Body:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

### Admin Endpoints

#### GET /api/admin/dashboard (Admin Only)
Get admin dashboard statistics.

**Response:**
```json
{
  "statistics": {
    "total_users": 150,
    "active_users": 142,
    "total_products": 45,
    "total_orders": 89,
    "total_revenue": 15420.50
  },
  "recent_orders": [...],
  "low_stock_products": [...]
}
```

#### GET /api/admin/users (Admin Only)
Get all users with filtering.

#### PUT /api/admin/users/{user_id}/role (Admin Only)
Update user role.

#### GET /api/admin/orders/all (Admin Only)
Get all orders with filtering.

#### PUT /api/admin/orders/{order_id}/status (Admin Only)
Update order status.

## Error Responses

The API returns standard HTTP status codes and error messages:

### 400 Bad Request
```json
{
  "detail": "Invalid input data",
  "error_code": "VALIDATION_ERROR"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication failed",
  "error_code": "AUTH_ERROR"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions",
  "error_code": "PERMISSION_ERROR"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found",
  "error_code": "NOT_FOUND"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

- **Authentication endpoints**: 5 requests per minute
- **General API**: 100 requests per minute
- **Admin endpoints**: 50 requests per minute

## Pagination

List endpoints support pagination with `skip` and `limit` parameters:

```
GET /api/products/?skip=20&limit=10
```

## Interactive Documentation

Visit `/docs` for interactive Swagger UI documentation or `/redoc` for ReDoc documentation.
