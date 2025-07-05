#!/bin/bash

# GPUStack UI Production Deployment Script for Mac Studio Ultra 3
# Optimized for macOS and M3 Ultra chip

set -e  # Exit on any error

echo "🍎 GPUStack UI Production Deployment for Mac Studio Ultra 3"
echo "=========================================================="

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS. Current OS: $OSTYPE"
    exit 1
fi

# Check if Docker Desktop is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker Desktop is not running. Please start Docker Desktop first."
    echo "   You can find Docker Desktop in your Applications folder."
    exit 1
fi

# Check Docker resources
echo "🔍 Checking Docker Desktop resources..."
DOCKER_MEMORY=$(docker system info --format '{{.MemTotal}}' 2>/dev/null | sed 's/[^0-9]//g')
if [ "$DOCKER_MEMORY" -lt 4000000000 ]; then  # Less than 4GB
    echo "⚠️  Warning: Docker Desktop has less than 4GB allocated."
    echo "   Recommended: 8-16GB for optimal performance on Mac Studio Ultra 3"
    echo "   Go to Docker Desktop → Settings → Resources → Memory"
fi

# Create production environment file if it doesn't exist
if [ ! -f .env.prod ]; then
    echo "📝 Creating production environment file..."
    cp .env.example .env.prod
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
mkdir -p logs uploads data nginx/ssl monitoring/grafana/provisioning

# Set proper permissions for macOS
chmod 755 logs uploads data
chmod 644 .env.prod

# Create self-signed SSL certificate for local development
if [ ! -f nginx/ssl/cert.pem ]; then
    echo "🔐 Creating self-signed SSL certificate for local development..."
    mkdir -p nginx/ssl
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    
    echo "✅ SSL certificate created"
fi

# Create monitoring configuration
if [ ! -f monitoring/prometheus.yml ]; then
    echo "📊 Creating Prometheus configuration..."
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'gpustack-ui'
    static_configs:
      - targets: ['backend:8001']
    metrics_path: '/api/health'
    scrape_interval: 30s
EOF
fi

# Stop existing deployment if running
echo "🛑 Stopping existing deployment..."
docker-compose -f docker-compose.mac-prod.yml --env-file .env.prod down || true

# Clean up old containers and images (optional)
read -p "Do you want to clean up old containers and images? (y/n): " cleanup
if [[ $cleanup =~ ^[Yy]$ ]]; then
    echo "🧹 Cleaning up old containers and images..."
    docker system prune -f
    docker image prune -f
fi

# Start production deployment
echo "🚀 Starting production deployment for Mac Studio Ultra 3..."
docker-compose -f docker-compose.mac-prod.yml --env-file .env.prod up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 45  # Increased wait time for Mac Studio Ultra 3

# Health check
echo "🏥 Performing health checks..."
if curl -f -k https://localhost/api/health > /dev/null 2>&1; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    echo "📋 Backend logs:"
    docker logs gpustack-ui-backend-mac-prod --tail 20
    echo ""
    echo "🔍 Troubleshooting tips:"
    echo "   1. Check if Docker Desktop has enough resources allocated"
    echo "   2. Verify .env.prod configuration"
    echo "   3. Check container logs: docker logs gpustack-ui-backend-mac-prod"
    exit 1
fi

# Show deployment status
echo "📊 Deployment status:"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

# Show resource usage
echo ""
echo "💾 Resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo ""
echo "🎉 Production deployment completed successfully!"
echo ""
echo "📱 Access your application:"
echo "   Frontend: https://localhost"
echo "   Backend API: https://localhost/api"
echo "   Health Check: https://localhost/health"
echo "   API Documentation: https://localhost/docs"
echo ""
echo "📊 Monitoring (optional):"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker logs gpustack-ui-backend-mac-prod -f"
echo "   Stop deployment: docker-compose -f docker-compose.mac-prod.yml down"
echo "   Update deployment: ./deploy-mac-production.sh"
echo "   Monitor resources: docker stats"
echo ""
echo "🔧 Performance tips for Mac Studio Ultra 3:"
echo "   - Ensure Docker Desktop has 8-16GB RAM allocated"
echo "   - Use 4-8 CPU cores for Docker"
echo "   - Enable 'Use the new Virtualization framework' in Docker Desktop"
echo "   - Monitor Activity Monitor for system resource usage"
echo "" 