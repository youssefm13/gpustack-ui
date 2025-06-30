# GPUStack UI v2.5.0 - Production Deployment Guide

This guide provides comprehensive instructions for deploying GPUStack UI v2.5.0 to production environments.

## 🚀 What's New in v2.5.0

- **OCR Support**: Full Tesseract OCR integration for image text extraction
- **Enhanced File Processing**: Support for image files with automatic text extraction
- **Improved Configuration Management**: Environment-based configuration system
- **Production-Ready Features**: Enhanced security, logging, and performance optimizations

## 📋 Prerequisites

- Docker and Docker Compose installed
- GPUStack server running and accessible
- Domain name configured (for SSL deployment)
- Minimum 4GB RAM, 2 CPU cores recommended

## 🔧 Configuration Requirements

### Required API Keys and Settings

GPUStack UI v2.5.0 uses environment variables for configuration. You need to configure the following:

#### 1. GPUStack API Configuration (Required)
```env
GPUSTACK_API_BASE=http://your-gpustack-server:port
GPUSTACK_API_TOKEN=your_gpustack_api_token
```

**How to obtain GPUStack API Token:**
1. Access your GPUStack web interface
2. Navigate to Settings → API Keys or Authentication
3. Generate a new API token
4. Copy the token (format: `gpustack_xxxxx_xxxxxx`)

#### 2. Security Configuration (Critical)
```env
JWT_SECRET_KEY=your-secure-32-character-secret
JWT_ALGORITHM=HS256
```

**Generate secure JWT secret:**
```bash
# Using OpenSSL
openssl rand -hex 32

# Using Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### 3. Tavily Search API (Optional)
```env
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx
```

**How to obtain Tavily API Key:**
1. Visit [Tavily.com](https://tavily.com)
2. Sign up for an account
3. Go to your dashboard/API section
4. Generate an API key

*Note: This is optional. Web search functionality will be disabled if not provided.*

## 🐳 Production Deployment Options

### Option 1: Docker Compose (Recommended)

#### Step 1: Clone and Setup
```bash
git clone https://github.com/youssefm13/gpustack-ui.git
cd gpustack-ui
git checkout v2.5.0
```

#### Step 2: Create Production Environment File
```bash
cp .env.production.template .env.prod
```

Edit `.env.prod` with your configuration:
```env
# Environment
ENV=production

# JWT Authentication (CHANGE THESE!)
JWT_SECRET_KEY=your-ultra-secure-production-jwt-secret-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# GPUStack API Configuration (REQUIRED)
GPUSTACK_API_BASE=http://192.168.1.231:80
GPUSTACK_API_TOKEN=gpustack_your_actual_token_here

# Tavily Search API (OPTIONAL)
TAVILY_API_KEY=tvly-your-api-key-here

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8001
WORKERS=4
LOG_LEVEL=warning

# Application Configuration
APPLICATION_URL=https://your-domain.com

# File Upload
MAX_FILE_SIZE_MB=100
UPLOAD_DIR=/app/uploads

# Security
CORS_ORIGINS=["https://your-domain.com"]
ALLOWED_HOSTS=["your-domain.com"]
```

#### Step 3: Update Frontend Configuration
Edit `frontend/public/config.js`:
```javascript
window.CONFIG = {
    BACKEND_URL: 'https://your-domain.com:8001'  // Your production backend URL
};
```

#### Step 4: Deploy with Docker Compose
```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose logs -f
```

### Option 2: Manual Installation

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract for OCR support
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# macOS:
brew install tesseract

# CentOS/RHEL:
sudo yum install tesseract tesseract-langpack-eng
```

#### Environment Configuration
```bash
# Copy and edit environment file
cp ../.env.production.template .env
nano .env  # Configure as shown above
```

#### Start Backend
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

#### Frontend Setup
```bash
cd ../frontend/public
# Update config.js with your backend URL
nano config.js

# Serve with nginx, Apache, or any static server
# Example with Python:
python -m http.server 3000
```

## 🔒 SSL/HTTPS Setup (Recommended)

### Using Nginx Reverse Proxy
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Using Let's Encrypt (Free SSL)
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🧪 Testing Your Deployment

### 1. Health Checks
```bash
# Backend health
curl https://your-domain.com:8001/api/health

# Frontend access
curl https://your-domain.com
```

### 2. API Testing
```bash
# Test models endpoint
curl https://your-domain.com:8001/api/models

# Test file upload (with authentication if enabled)
curl -X POST -F "file=@test.png" https://your-domain.com:8001/api/files/upload
```

### 3. OCR Testing
1. Access your deployment in a web browser
2. Upload an image containing text
3. Send a message asking about the image content
4. Verify the AI responds with extracted text

## 🔧 Configuration Service Management

GPUStack UI v2.5.0 includes a built-in configuration service accessible through the web interface:

### Accessing Configuration
1. Log into your GPUStack UI
2. Navigate to Settings → Configuration
3. Configure API keys and external services
4. Settings are automatically saved and applied

### Configuration Options Available:
- **GPUStack API Settings**: Server URL and authentication
- **Search API Settings**: Tavily API key for web search
- **File Processing Settings**: Upload limits and OCR options
- **Security Settings**: JWT configuration and CORS settings

## 🐛 Troubleshooting

### Common Issues

#### "Backend Disconnected" Error
- Check backend service is running: `docker-compose ps`
- Verify firewall allows port 8001
- Check frontend config.js points to correct backend URL

#### "No models available"
- Verify GPUStack server is running and accessible
- Check `GPUSTACK_API_BASE` and `GPUSTACK_API_TOKEN` in environment
- Test direct API access: `curl http://your-gpustack:port/v1/models`

#### OCR Not Working
- Ensure Tesseract is installed in the container/system
- Check file upload size limits
- Verify supported image formats (PNG, JPG, TIFF, BMP)

#### Authentication Issues
- Verify JWT_SECRET_KEY is set and secure
- Check browser storage for auth tokens
- Clear browser cache and cookies

### Logging and Monitoring
```bash
# Check application logs
docker-compose logs -f backend

# Monitor system resources
docker stats

# Check disk usage
df -h
```

## 🔄 Updates and Maintenance

### Updating to New Version
```bash
# Stop services
docker-compose down

# Pull latest changes
git pull origin master
git checkout v[NEW_VERSION]

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

### Backup Recommendations
- Backup configuration files (`.env.prod`, `config.js`)
- Backup user data and uploaded files
- Backup database files if using persistent storage

## 📊 Performance Optimization

### Production Settings
- Use 4+ workers for backend
- Enable Redis for caching (optional)
- Configure appropriate file upload limits
- Monitor memory usage with multiple concurrent users

### Scaling Considerations
- Use load balancer for multiple backend instances
- Consider database separation for high-traffic deployments
- Monitor API response times and adjust worker count

## 🛡️ Security Best Practices

1. **Use strong JWT secrets** (minimum 32 characters)
2. **Enable HTTPS** in production
3. **Restrict CORS origins** to your domain only
4. **Regular security updates** for dependencies
5. **Monitor logs** for suspicious activity
6. **Use environment variables** for sensitive data
7. **Regular backups** of configuration and data

## 📞 Support

For issues or questions:
- GitHub Issues: [https://github.com/youssefm13/gpustack-ui/issues](https://github.com/youssefm13/gpustack-ui/issues)
- Documentation: Check the `/docs` directory
- API Documentation: Visit `/docs` endpoint when backend is running

---

**GPUStack UI v2.5.0** - Production ready with OCR support and enhanced configuration management.
