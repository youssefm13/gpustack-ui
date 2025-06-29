#!/bin/bash

# Manual Docker Deployment for GPUStack UI
# Use this if you prefer manual container management

echo "🐳 Manual Docker Deployment for GPUStack UI"

# Build backend image
echo "🔨 Building backend image..."
docker build -f backend/Dockerfile.prod -t gpustack-ui-backend:prod backend/

# Build frontend image (if you have one)
# docker build -f frontend/Dockerfile.prod -t gpustack-ui-frontend:prod frontend/

# Create network
echo "🌐 Creating Docker network..."
docker network create gpustack-network || true

# Start Redis (optional but recommended)
echo "🔴 Starting Redis..."
docker run -d \
  --name gpustack-redis \
  --network gpustack-network \
  -p 6379:6379 \
  -v redis_data:/data \
  --restart unless-stopped \
  redis:7-alpine redis-server --appendonly yes

# Start backend
echo "🖥️  Starting backend..."
docker run -d \
  --name gpustack-ui-backend \
  --network gpustack-network \
  -p 8001:8001 \
  --env-file .env.prod \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/uploads:/app/uploads \
  --restart unless-stopped \
  gpustack-ui-backend:prod

# Wait and check health
sleep 10
echo "🏥 Checking backend health..."
if curl -f http://localhost:8001/api/health; then
    echo "✅ Backend is healthy!"
else
    echo "❌ Backend health check failed"
    docker logs gpustack-ui-backend --tail 20
fi

echo "🎉 Manual deployment completed!"
echo "Backend: http://localhost:8001"
echo "Health: http://localhost:8001/api/health"
