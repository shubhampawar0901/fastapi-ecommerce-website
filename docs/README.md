# FastAPI E-commerce API

A comprehensive e-commerce REST API built with FastAPI, featuring user authentication, product management, shopping cart functionality, and order processing.

## 🚀 Features

### Core Functionality
- **User Authentication & Authorization**: JWT-based authentication with role-based access control
- **Product Catalog**: Complete product management with categories, inventory tracking, and search
- **Shopping Cart**: Session-based cart for guests and persistent cart for authenticated users
- **Order Management**: Full order lifecycle from creation to delivery tracking
- **Admin Panel**: Administrative endpoints for system management

### Technical Features
- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **SQLAlchemy ORM**: Database abstraction with support for SQLite (dev) and PostgreSQL (prod)
- **Pydantic Validation**: Request/response validation and serialization
- **JWT Authentication**: Secure token-based authentication
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Comprehensive Logging**: Structured logging for monitoring and debugging

## 📁 Project Structure

```
fastapi-ecommerce-website/
├── main.py                 # FastAPI application entry point
├── database.py            # Database configuration and session management
├── auth.py                # Authentication utilities and JWT handling
├── schemas.py             # Pydantic models for request/response validation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # Project documentation
├── models/               # SQLAlchemy database models
│   ├── __init__.py
│   ├── user.py          # User model with roles and authentication
│   ├── product.py       # Product and Category models
│   ├── cart.py          # Shopping cart and cart items
│   └── order.py         # Order and order items with status tracking
└── routers/             # API route handlers
    ├── __init__.py
    ├── auth.py          # Authentication endpoints
    ├── products.py      # Product and category management
    ├── cart.py          # Shopping cart operations
    ├── orders.py        # Order management
    ├── users.py         # User profile management
    └── admin.py         # Administrative operations
```

## 🛠 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/shubhampawar0901/fastapi-ecommerce-website.git
   cd fastapi-ecommerce-website
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Run the application**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - User logout

### Products
- `GET /api/products/` - List products with filtering
- `GET /api/products/{id}` - Get product by ID
- `GET /api/products/slug/{slug}` - Get product by slug
- `POST /api/products/` - Create product (Admin)
- `PUT /api/products/{id}` - Update product (Admin)
- `DELETE /api/products/{id}` - Delete product (Admin)

### Categories
- `GET /api/products/categories` - List categories
- `GET /api/products/categories/{id}` - Get category by ID
- `POST /api/products/categories` - Create category (Admin)

### Shopping Cart
- `GET /api/cart/` - Get current cart
- `POST /api/cart/items` - Add item to cart
- `PUT /api/cart/items/{id}` - Update cart item
- `DELETE /api/cart/items/{id}` - Remove cart item
- `DELETE /api/cart/clear` - Clear cart

### Orders
- `GET /api/orders/` - Get user's orders
- `GET /api/orders/{id}` - Get order by ID
- `POST /api/orders/` - Create order
- `POST /api/orders/{id}/cancel` - Cancel order

### User Management
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/change-password` - Change password
- `DELETE /api/users/account` - Delete account

### Admin
- `GET /api/admin/dashboard` - Admin dashboard
- `GET /api/admin/users` - List all users
- `PUT /api/admin/users/{id}/role` - Update user role
- `GET /api/admin/system/health` - System health check

## 🗄 Database Schema

### User Roles
- **CUSTOMER**: Regular users who can browse and purchase
- **STAFF**: Staff members with limited admin access
- **ADMIN**: Full administrative access

### Order Status Flow
```
PENDING → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
    ↓
CANCELLED (from PENDING, CONFIRMED, PROCESSING)
```

### Payment Status
- **PENDING**: Payment not yet processed
- **PAID**: Payment successful
- **FAILED**: Payment failed
- **REFUNDED**: Payment refunded

## 🚀 Deployment to Render

### Prerequisites
- GitHub account with repository
- Render account (render.com)

### Deployment Steps

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Render Web Service**
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository

3. **Configure Build Settings**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

4. **Set Environment Variables**
   ```
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=postgresql://user:password@host:port/database
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=production
   ```

5. **Database Setup**
   - Create PostgreSQL database on Render
   - Update DATABASE_URL environment variable
   - Database tables will be created automatically on first run

### Production Considerations
- Use strong SECRET_KEY
- Configure proper CORS origins
- Set up database backups
- Monitor application logs
- Implement rate limiting
- Add SSL certificate

## 🧪 Testing

### Run Tests
```bash
pytest
```

### Test Coverage
```bash
pytest --cov=.
```

### Manual Testing
Use the interactive API documentation at `/docs` to test endpoints manually.

## 📊 Monitoring & Logging

### Health Checks
- Application: `GET /health`
- Admin: `GET /api/admin/system/health`

### Logging
- Structured logging with timestamps
- Different log levels (INFO, ERROR, DEBUG)
- Request/response logging
- Error tracking and debugging

## 🔒 Security Features

- **Password Hashing**: Bcrypt for secure password storage
- **JWT Tokens**: Secure authentication with expiration
- **Role-based Access**: Different permission levels
- **Input Validation**: Pydantic models for data validation
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Configuration**: Controlled cross-origin access

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: support@example.com

## 🔄 Version History

- **v1.0.0** - Initial release with core e-commerce functionality
- Complete user authentication and authorization
- Product catalog with categories
- Shopping cart functionality
- Order management system
- Admin panel for system management

---

**Built with ❤️ using FastAPI**
