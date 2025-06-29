# GPUStack UI Deployment Guide

This guide covers different deployment options for the GPUStack UI, from development to production environments.

## Quick Start

### Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/youssefm13/gpustack-ui.git
   cd gpustack-ui
   ```

2. **Copy environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Production Environment

1. **Copy production environment configuration**
   ```bash
   cp .env.example .env.prod
   # Edit .env.prod with production values
   ```

2. **Start production deployment**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Environment Configuration

### Required Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GPUSTACK_API_BASE` | GPUStack API endpoint | `http://localhost:8080` | Yes |
| `TAVILY_API_KEY` | Tavily search API key | - | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | - | Yes (Production) |

### Optional Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment mode | `development` |
| `BACKEND_PORT` | Backend server port | `8001` |
| `WORKERS` | Number of worker processes | `3` |
| `LOG_LEVEL` | Logging level | `info` |
| `MAX_FILE_SIZE_MB` | Max upload file size | `50` |

## Deployment Options

### 1. Docker Compose (Recommended)

#### Development
```bash
# Standard development setup
docker-compose up -d

# With custom environment file
docker-compose --env-file .env.dev up -d
```

#### Production
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# With custom environment file
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### 2. Manual Docker Build

#### Backend
```bash
# Development build
docker build -t gpustack-ui-backend:dev ./backend

# Production build
docker build -f ./backend/Dockerfile.prod -t gpustack-ui-backend:prod ./backend

# Run container
docker run -d \
  --name gpustack-ui-backend \
  -p 8001:8001 \
  --env-file .env \
  gpustack-ui-backend:prod
```

#### Frontend
```bash
# Build and run frontend
docker build -t gpustack-ui-frontend:prod ./frontend
docker run -d \
  --name gpustack-ui-frontend \
  -p 80:80 \
  gpustack-ui-frontend:prod
```

### 3. Native Python Deployment

#### Prerequisites
- Python 3.10+ 
- Node.js 18+ (for frontend)
- Redis (optional, for caching)

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Run production server
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build
npm run start
```

## Production Considerations

### Security

1. **Environment Variables**
   - Use strong, unique JWT secret keys
   - Store sensitive credentials in secure secret management
   - Never commit `.env` files to version control

2. **HTTPS Configuration**
   - Use SSL certificates (Let's Encrypt recommended)
   - Configure reverse proxy (Nginx) for SSL termination
   - Enable HSTS headers

3. **Access Control**
   - Configure firewall rules
   - Use non-root users in containers
   - Implement rate limiting

### Performance

1. **Backend Optimization**
   - Use multiple workers (4+ for production)
   - Enable async processing
   - Configure connection pooling

2. **Database & Caching**
   - Use Redis for session storage and caching
   - Consider PostgreSQL for persistent data
   - Implement connection pooling

3. **Load Balancing**
   - Use Nginx as reverse proxy
   - Configure health checks
   - Implement graceful shutdowns

### Monitoring

1. **Health Checks**
   ```bash
   # Backend health
   curl http://localhost:8001/api/health
   
   # Container health
   docker ps --format "table {{.Names}}\t{{.Status}}"
   ```

2. **Logging**
   - Configure centralized logging
   - Use structured logging format
   - Set appropriate log levels

3. **Metrics**
   - Monitor resource usage
   - Track API response times
   - Set up alerting

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster
- kubectl configured
- Docker images pushed to registry

### Basic Deployment

1. **Create namespace**
   ```bash
   kubectl create namespace gpustack-ui
   ```

2. **Deploy backend**
   ```yaml
   # backend-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: gpustack-ui-backend
     namespace: gpustack-ui
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: gpustack-ui-backend
     template:
       metadata:
         labels:
           app: gpustack-ui-backend
       spec:
         containers:
         - name: backend
           image: gpustack-ui-backend:prod
           ports:
           - containerPort: 8001
           env:
           - name: ENV
             value: "production"
           - name: GPUSTACK_API_BASE
             valueFrom:
               configMapKeyRef:
                 name: gpustack-config
                 key: api-base
           - name: JWT_SECRET_KEY
             valueFrom:
               secretKeyRef:
                 name: gpustack-secrets
                 key: jwt-secret
   ```

3. **Apply configurations**
   ```bash
   kubectl apply -f backend-deployment.yaml
   kubectl apply -f frontend-deployment.yaml
   kubectl apply -f services.yaml
   ```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if services are running: `docker ps`
   - Verify port mappings
   - Check firewall settings

2. **Authentication Errors**
   - Verify JWT secret key configuration
   - Check GPUStack API connectivity
   - Validate environment variables

3. **File Upload Issues**
   - Check file size limits
   - Verify upload directory permissions
   - Monitor disk space

### Debug Commands

```bash
# Check container logs
docker logs gpustack-ui-backend
docker logs gpustack-ui-frontend

# Check container resource usage
docker stats

# Execute commands in container
docker exec -it gpustack-ui-backend /bin/bash

# Test API endpoints
curl -f http://localhost:8001/api/health
curl -f http://localhost:8001/api/models
```

### Performance Tuning

1. **Backend Performance**
   ```bash
   # Increase workers for production
   docker-compose -f docker-compose.prod.yml \
     -e WORKERS=6 up -d
   
   # Monitor resource usage
   docker stats gpustack-ui-backend
   ```

2. **Database Optimization**
   - Use connection pooling
   - Configure appropriate timeouts
   - Monitor query performance

## Backup and Recovery

### Data Backup

1. **Database Backup**
   ```bash
   # SQLite backup
   docker cp gpustack-ui-backend:/app/gpustack_ui.db ./backup/
   
   # PostgreSQL backup
   docker exec postgres pg_dump -U user gpustack_ui > backup.sql
   ```

2. **Configuration Backup**
   ```bash
   # Backup environment files
   cp .env backup/env-$(date +%Y%m%d)
   cp docker-compose.yml backup/
   ```

### Recovery Process

1. **Restore Database**
   ```bash
   # Stop services
   docker-compose down
   
   # Restore database
   docker cp ./backup/gpustack_ui.db gpustack-ui-backend:/app/
   
   # Restart services
   docker-compose up -d
   ```

## Support

For deployment issues and questions:

1. Check the [GitHub Issues](https://github.com/youssefm13/gpustack-ui/issues)
2. Review the troubleshooting section above
3. Check container logs for specific error messages
4. Verify environment configuration matches requirements
