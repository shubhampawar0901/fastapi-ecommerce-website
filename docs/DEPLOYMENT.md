# Deployment Guide for FastAPI E-commerce Application

This guide provides step-by-step instructions for deploying the FastAPI e-commerce application to Render cloud platform.

## Prerequisites

- GitHub account
- Render account (render.com)
- Git installed locally
- Python 3.8+ installed locally

## Local Testing

Before deployment, ensure the application works locally:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize sample data**
   ```bash
   python init_data.py
   ```

3. **Run the application**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Test endpoints**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Products: http://localhost:8000/api/products/

## GitHub Repository Setup

1. **Initialize Git repository** (if not already done)
   ```bash
   git init
   git add .
   git commit -m "Initial commit: FastAPI e-commerce application"
   ```

2. **Create GitHub repository**
   - Go to GitHub and create a new repository
   - Name it `fastapi-ecommerce-website`
   - Make it public or private (Render supports both)

3. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/yourusername/fastapi-ecommerce-website.git
   git branch -M main
   git push -u origin main
   ```

## Render Deployment

### Method 1: Using Render Dashboard

1. **Create Web Service**
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Build Settings**
   - **Name**: `fastapi-ecommerce-api`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   ```
   SECRET_KEY=your-super-secret-production-key-here
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ENVIRONMENT=production
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

4. **Create PostgreSQL Database**
   - Click "New" → "PostgreSQL"
   - Name: `fastapi-ecommerce-db`
   - Plan: Free (or higher for production)
   - Copy the connection string to DATABASE_URL

### Method 2: Using render.yaml (Infrastructure as Code)

1. **Use the provided render.yaml**
   - The repository includes a `render.yaml` file
   - This automatically configures both web service and database

2. **Deploy via Blueprint**
   - In Render Dashboard, click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically create all services

## Environment Variables Configuration

### Required Variables
- `SECRET_KEY`: JWT secret key (generate a strong random string)
- `DATABASE_URL`: PostgreSQL connection string from Render
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration (default: 7)

### Optional Variables
- `ENVIRONMENT`: Set to "production"
- `ALLOWED_ORIGINS`: CORS origins (comma-separated)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)

## Database Setup

1. **Automatic Table Creation**
   - Tables are created automatically on first run
   - The application uses SQLAlchemy with auto-migration

2. **Initialize Sample Data** (Optional)
   - SSH into your Render service or use a one-time job
   - Run: `python init_data.py`
   - This creates sample products and admin user

## Post-Deployment Verification

1. **Check Application Health**
   ```bash
   curl https://your-app-name.onrender.com/health
   ```

2. **Test API Endpoints**
   - Visit: `https://your-app-name.onrender.com/docs`
   - Test user registration and login
   - Verify product listings work

3. **Admin Access**
   - Email: `admin@ecommerce.com`
   - Password: `admin123`
   - Change these credentials immediately in production!

## Production Considerations

### Security
- [ ] Change default admin credentials
- [ ] Use strong SECRET_KEY
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS (automatic on Render)
- [ ] Set up rate limiting

### Performance
- [ ] Upgrade to paid Render plan for better performance
- [ ] Add Redis for caching and sessions
- [ ] Optimize database queries
- [ ] Add CDN for static assets

### Monitoring
- [ ] Set up application logging
- [ ] Configure error tracking (Sentry)
- [ ] Monitor database performance
- [ ] Set up uptime monitoring

### Backup
- [ ] Configure database backups
- [ ] Set up automated backups schedule
- [ ] Test backup restoration process

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check requirements.txt for correct versions
   - Ensure Python version compatibility
   - Review build logs in Render dashboard

2. **Database Connection Issues**
   - Verify DATABASE_URL format
   - Check database service status
   - Ensure database and web service are in same region

3. **Environment Variable Issues**
   - Verify all required variables are set
   - Check for typos in variable names
   - Ensure SECRET_KEY is properly generated

4. **Import Errors**
   - Check Python path issues
   - Verify all dependencies are in requirements.txt
   - Review application logs

### Debugging Commands

```bash
# Check application logs
render logs --service your-service-name

# Connect to database
render shell --service your-database-name

# Run one-time job
render job create --service your-service-name --command "python init_data.py"
```

## Scaling and Optimization

### Horizontal Scaling
- Upgrade Render plan for auto-scaling
- Use load balancer for multiple instances
- Implement stateless session management

### Database Optimization
- Add database indexes for frequently queried fields
- Implement connection pooling
- Use read replicas for heavy read workloads

### Caching
- Add Redis for session storage
- Implement API response caching
- Use CDN for static content

## Support and Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Application Repository](https://github.com/yourusername/fastapi-ecommerce-website)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
