#!/bin/bash

# GPUStack UI Production Deployment Script
# Run this script on your production server

set -e  # Exit on any error

echo "🚀 Starting GPUStack UI Production Deployment..."

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then 
    echo "⚠️  Warning: Running as root. Consider using a non-root user for security."
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create production environment file if it doesn't exist
if [ ! -f .env.prod ]; then
    echo "📝 Creating production environment file..."
    cp .env.production.template .env.prod
    echo "⚠️  IMPORTANT: Edit .env.prod with your actual production values!"
    echo "   Required values to update:"
    echo "   - GPUSTACK_API_BASE"
    echo "   - GPUSTACK_API_TOKEN" 
    echo "   - TAVILY_API_KEY"
    echo "   - JWT_SECRET_KEY"
    echo "   - Your domain URLs"
    read -p "Press Enter when you've updated .env.prod..."
fi

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p logs uploads

# Set proper permissions
chmod 755 logs uploads

# Pull latest images (if using pre-built images)
echo "📥 Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull || echo "⚠️  Some images may need to be built locally"

# Stop existing deployment if running
echo "🛑 Stopping existing deployment..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod down || true

# Start production deployment
echo "🚀 Starting production deployment..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Health check
echo "🏥 Performing health checks..."
if curl -f http://localhost:8001/api/health > /dev/null 2>&1; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    echo "📋 Backend logs:"
    docker logs gpustack-ui-backend-prod --tail 20
    exit 1
fi

# Show deployment status
echo "📊 Deployment status:"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo ""
echo "🎉 Production deployment completed successfully!"
echo ""
echo "📱 Access your application:"
echo "   Frontend: http://localhost (or your domain)"
echo "   Backend API: http://localhost:8001"
echo "   Health Check: http://localhost:8001/api/health"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker logs gpustack-ui-backend-prod"
echo "   Stop deployment: docker-compose -f docker-compose.prod.yml down"
echo "   Update deployment: ./deploy-production.sh"
echo ""
