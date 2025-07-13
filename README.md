# FastAPI E-commerce API

A production-grade e-commerce REST API built with FastAPI, featuring comprehensive business logic, security, and deployment automation.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Setup
```bash
# Clone the repository
git clone https://github.com/shubhampawar0901/fastapi-ecommerce-website.git
cd fastapi-ecommerce-website

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Activate virtual environment
source venv/bin/activate

# Start development server
uvicorn main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## ✨ Features

- 🔐 **JWT Authentication** - Secure user authentication and authorization
- 🛍️ **Product Catalog** - Complete product and category management
- 🛒 **Shopping Cart** - Session-based cart for guests and persistent for users
- 📦 **Order Management** - Full order lifecycle with status tracking
- 👨‍💼 **Admin Panel** - Administrative dashboard and management tools
- 🔍 **Search & Filtering** - Advanced product search and filtering
- 📱 **RESTful API** - Clean, documented REST API endpoints
- 🧪 **Comprehensive Testing** - Unit and integration test suite
- 🚀 **Production Ready** - Deployment automation and monitoring

## 📁 Project Structure

```
fastapi-ecommerce-website/
├── main.py                    # Application entry point
├── app/                       # Main application package
│   ├── core/                  # Core components (config, database, security)
│   ├── api/                   # API route handlers
│   ├── models/                # Database models
│   ├── schemas/               # Pydantic validation schemas
│   ├── services/              # Business logic services
│   └── utils/                 # Utility functions
├── tests/                     # Test suite
├── config/                    # Environment configurations
├── scripts/                   # Deployment and utility scripts
└── docs/                      # Documentation
```

See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for detailed structure explanation.

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/me` - Current user info

### Products
- `GET /api/products/` - List products with filtering
- `GET /api/products/{id}` - Get product details
- `POST /api/products/` - Create product (Admin)
- `PUT /api/products/{id}` - Update product (Admin)

### Shopping Cart
- `GET /api/cart/` - Get current cart
- `POST /api/cart/items` - Add item to cart
- `PUT /api/cart/items/{id}` - Update cart item
- `DELETE /api/cart/items/{id}` - Remove cart item

### Orders
- `GET /api/orders/` - Get user orders
- `POST /api/orders/` - Create order
- `GET /api/orders/{id}` - Get order details

See [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for complete API reference.

## 🧪 Testing

```bash
# Run all tests
./scripts/test.sh

# Run specific test types
pytest tests/unit/ -v          # Unit tests
pytest tests/integration/ -v   # Integration tests

# Run with coverage
pytest --cov=app --cov-report=html
```

## 🚀 Deployment

### Local Development
```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Using the start script
./scripts/start.sh
```

### Production Deployment

#### Render Cloud Platform
See [docs/RENDER_DEPLOYMENT_GUIDE.md](docs/RENDER_DEPLOYMENT_GUIDE.md) for step-by-step deployment instructions.

#### Docker
```bash
# Build image
docker build -t fastapi-ecommerce .

# Run container
docker run -p 8000:8000 -e DATABASE_URL=your_db_url fastapi-ecommerce
```

## ⚙️ Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# Application
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host/db

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=https://yourdomain.com
```

### Environment-Specific Configs
- `config/development.env` - Development settings
- `config/production.env` - Production settings  
- `config/testing.env` - Testing settings

## 📊 Project Statistics

- **Lines of Code**: 5,200+
- **Test Coverage**: 17 tests (100% passing)
- **API Endpoints**: 30+
- **Database Models**: 6 comprehensive models
- **Documentation**: Complete with guides

## 🔒 Security Features

- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation with Pydantic
- SQL injection protection
- CORS configuration
- Environment variable security

## 📚 Documentation

- [Project Structure](docs/PROJECT_STRUCTURE.md) - Detailed folder structure
- [API Documentation](docs/API_DOCUMENTATION.md) - Complete API reference
- [Deployment Guide](docs/RENDER_DEPLOYMENT_GUIDE.md) - Render deployment
- [Deployment Summary](docs/DEPLOYMENT_SUMMARY.md) - Project overview

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/shubhampawar0901/fastapi-ecommerce-website/issues)
- 📖 Documentation: [docs/](docs/)

---

**Built with ❤️ using FastAPI and modern Python practices**
