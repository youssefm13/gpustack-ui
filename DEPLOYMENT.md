# GPUStack UI v2.0.0 - Deployment Guide

This guide covers everything needed to deploy GPUStack UI v2.0.0 on a new machine.

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (recommended) OR
- **Python 3.11+** and **Node.js** (manual setup)
- **GPUStack server** running and accessible
- **Tavily API key** (optional, for web search)

---

## 📦 Method 1: Docker Deployment (Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/gpustack-ui.git
cd gpustack-ui
git checkout v2.0.0  # Use the stable v2.0 release
```

### 2. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env
```

**Required `.env` configuration:**
```env
# Required: Your GPUStack server URL
GPUSTACK_API_URL=http://YOUR_GPUSTACK_IP:8000/v1/chat/completions

# Optional: Tavily API key for web search (get from https://tavily.com)
TAVILY_API_KEY=your-tavily-api-key-here

# Optional: GPUStack API key if authentication is required
GPUSTACK_API_KEY=your-gpustack-api-key
```

### 3. Configure Frontend Backend URL
```bash
# Edit the frontend configuration
nano frontend/public/config.js
```

Update the `BACKEND_URL` to point to your deployment:
```javascript
window.CONFIG = {
    // For local deployment
    BACKEND_URL: 'http://localhost:8001'
    
    // For remote deployment (replace with your server IP/domain)
    // BACKEND_URL: 'http://YOUR_SERVER_IP:8001'
    // BACKEND_URL: 'https://your-domain.com:8001'
};
```

### 4. Deploy with Docker Compose
```bash
# Build and start all services
docker-compose up -d

# Check logs to ensure everything is running
docker-compose logs -f
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **Health Check**: http://localhost:8001/health

---

## 🔧 Method 2: Manual Installation

### 1. Clone and Setup Backend
```bash
git clone https://github.com/your-username/gpustack-ui.git
cd gpustack-ui
git checkout v2.0.0

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
nano .env  # Configure as shown above
```

### 2. Start Backend Server
```bash
# From backend directory
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 3
```

### 3. Setup Frontend
```bash
# Open new terminal, from project root
cd frontend/public

# Configure backend URL
nano config.js  # Update BACKEND_URL as needed

# Serve with any static server (examples):
# Python
python -m http.server 3000

# Node.js (if you have it)
npx serve -p 3000

# Nginx (if installed)
# Point nginx to the frontend/public directory
```

---

## 🌐 Remote/Production Deployment

### Server Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB+ recommended (2GB minimum)
- **Storage**: 10GB+ for application and logs
- **Network**: Open ports 3000 (frontend) and 8001 (backend)

### 1. Update Configuration for Remote Access
```bash
# Update frontend config for remote access
nano frontend/public/config.js
```

```javascript
window.CONFIG = {
    // Use your server's public IP or domain
    BACKEND_URL: 'http://YOUR_SERVER_IP:8001'
    // Or with SSL: 'https://your-domain.com:8001'
};
```

### 2. Update Docker Compose for Production
```yaml
# docker-compose.prod.yml
services:
  backend:
    build: ./backend
    ports:
      - "8001:8000"
    environment:
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - GPUSTACK_API_URL=${GPUSTACK_API_URL}
      - GPUSTACK_API_KEY=${GPUSTACK_API_KEY}
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    restart: unless-stopped
    
  frontend:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./frontend/public:/usr/share/nginx/html:ro
    restart: unless-stopped
    depends_on:
      - backend
```

### 3. Deploy with Production Settings
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔐 Security Considerations

### Environment Variables
- **Never commit `.env` files** to version control
- **Use strong API keys** and rotate them regularly
- **Restrict GPUStack access** to known IPs if possible

### Network Security
```bash
# Example firewall rules (Ubuntu/Debian)
sudo ufw allow 22    # SSH
sudo ufw allow 3000  # Frontend
sudo ufw allow 8001  # Backend API
sudo ufw enable
```

### SSL/HTTPS (Recommended for Production)
```bash
# Use a reverse proxy like nginx with Let's Encrypt
# Example nginx configuration for SSL termination:
```

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🧪 Testing the Deployment

### 1. Health Check
```bash
curl http://localhost:8001/health
# Should return: {"status": "healthy", "timestamp": "...", "system": {...}}
```

### 2. Backend API Test
```bash
curl http://localhost:8001/
# Should return: {"message": "GPUStack LLM Backend is running!"}
```

### 3. Model Connectivity Test
```bash
curl http://localhost:8001/api/models
# Should return available models from your GPUStack server
```

### 4. Frontend Access
- Open http://localhost:3000 in browser
- Check that model selector shows available models
- Test file upload functionality
- Try a simple chat message

---

## 🔧 Troubleshooting

### Common Issues

#### "Backend Disconnected" Error
- **Check**: Backend is running on correct port (8001)
- **Check**: Frontend config.js points to correct backend URL
- **Check**: Firewall allows port 8001

#### "No models available"
- **Check**: GPUStack server is running and accessible
- **Check**: `GPUSTACK_API_URL` in .env is correct
- **Check**: Network connectivity to GPUStack server

#### File Upload Fails
- **Check**: Backend has sufficient disk space
- **Check**: File size under 50MB limit
- **Check**: Supported file types: PDF, DOCX, TXT, JPG, PNG

#### Web Search Not Working
- **Check**: `TAVILY_API_KEY` is set in .env
- **Check**: Tavily API key is valid and has credits
- **Note**: Web search is optional, chat works without it

### Debug Commands
```bash
# Check backend logs
docker-compose logs backend

# Check frontend logs
docker-compose logs frontend

# Check system resources
docker stats

# Check port availability
netstat -tulpn | grep :8001
netstat -tulpn | grep :3000

# Test backend directly
curl -v http://localhost:8001/health
```

### Performance Tuning
```bash
# Increase backend workers for better concurrency
# Edit docker-compose.yml:
command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 6

# Allocate more memory if needed
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

---

## 📋 Feature Overview

### ✅ What's Included in v2.0.0

**Core Features:**
- 💬 **AI Chat Interface** with streaming responses
- 📁 **File Processing** (PDF, DOCX, TXT, images)
- 🔍 **Web Search** integration via Tavily
- 🛑 **Stop Chat** functionality for long responses

**Export/Import System:**
- 📄 **Markdown Export** - Human-readable format
- 📝 **Plain Text Export** - Universal compatibility  
- 🔧 **JSON Export** - Complete data fidelity
- 📥 **Multi-format Import** - Auto-detects file type

**Performance & Monitoring:**
- ⚡ **Response Metrics** - Timing and token counts
- 🏥 **Health Monitoring** - System status endpoints
- 🔄 **Async Backend** - Better concurrency handling
- 📊 **Resource Monitoring** - CPU/memory usage

**Enhanced UX:**
- 🌙 **Dark/Light Theme** toggle
- 📱 **Responsive Design** for mobile/desktop
- 🎨 **Syntax Highlighting** for code blocks
- 📋 **Copy Buttons** for code snippets

---

## 🆙 Upgrading from v1.x

### From v1.0 to v2.0
```bash
# Backup your current deployment
docker-compose down
cp .env .env.backup

# Pull the new version
git fetch --tags
git checkout v2.0.0

# Update configuration if needed
# (Check if new environment variables were added)

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

### Breaking Changes
- **None** - v2.0 is backward compatible with v1.0 configurations
- **Enhanced**: File processing now returns richer metadata
- **New**: Additional optional environment variables for new features

---

## 📞 Support

### Getting Help
- **Issues**: Create GitHub issues for bugs or feature requests
- **Documentation**: Check README.md for basic usage
- **Logs**: Always include docker-compose logs when reporting issues

### Contributing
- **Fork** the repository
- **Create** a feature branch
- **Submit** pull requests to the `dev-improvements` branch

---

## 📄 License & Credits

- **License**: [Add your license here]
- **GPUStack**: https://github.com/gpustack/gpustack
- **Tavily**: https://tavily.com (for web search functionality)

---

**GPUStack UI v2.0.0** - Enhanced AI chat interface with advanced file processing and multi-format export capabilities.
