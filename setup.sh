#!/bin/bash

# GPUStack UI v2.0.0 - Quick Setup Script
# This script helps you quickly deploy GPUStack UI on a new machine

set -e

echo "🚀 GPUStack UI v2.0.0 - Quick Setup"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env configuration file..."
    cp .env.example .env
    
    echo ""
    echo "⚙️  Please configure your environment variables:"
    echo "   Edit .env file and set:"
    echo "   - GPUSTACK_API_URL (your GPUStack server URL)"
    echo "   - TAVILY_API_KEY (optional, for web search)"
    echo ""
    
    read -p "Do you want to edit .env now? (y/n): " edit_env
    if [[ $edit_env =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo "✅ .env file already exists"
fi

# Ask for frontend configuration
echo ""
echo "🌐 Frontend Configuration"
echo "Current backend URL in config.js:"
grep "BACKEND_URL" frontend/public/config.js | head -1

echo ""
echo "Choose deployment type:"
echo "1) Local deployment (localhost)"
echo "2) Remote deployment (custom IP/domain)"
echo "3) Keep current configuration"

read -p "Enter choice (1-3): " deployment_choice

case $deployment_choice in
    1)
        echo "Setting up for local deployment..."
        sed -i.bak "s|BACKEND_URL:.*|BACKEND_URL: 'http://localhost:8001'|" frontend/public/config.js
        echo "✅ Configured for local access"
        ;;
    2)
        read -p "Enter your server IP or domain: " server_address
        sed -i.bak "s|BACKEND_URL:.*|BACKEND_URL: 'http://${server_address}:8001'|" frontend/public/config.js
        echo "✅ Configured for remote access: $server_address"
        ;;
    3)
        echo "✅ Keeping current configuration"
        ;;
    *)
        echo "❌ Invalid choice, keeping current configuration"
        ;;
esac

# Build and start services
echo ""
echo "🏗️  Building and starting services..."

# Use docker-compose or docker compose based on availability
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

$DOCKER_COMPOSE down 2>/dev/null || true
$DOCKER_COMPOSE build --no-cache
$DOCKER_COMPOSE up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."

# Check backend
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Backend is running (http://localhost:8001)"
else
    echo "❌ Backend health check failed"
    echo "   Check logs: $DOCKER_COMPOSE logs backend"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running (http://localhost:3000)"
else
    echo "❌ Frontend health check failed"
    echo "   Check logs: $DOCKER_COMPOSE logs frontend"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📱 Access your GPUStack UI:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8001"
echo "   Health:   http://localhost:8001/health"
echo ""
echo "🔧 Useful commands:"
echo "   View logs:    $DOCKER_COMPOSE logs -f"
echo "   Stop:         $DOCKER_COMPOSE down"
echo "   Restart:      $DOCKER_COMPOSE restart"
echo "   Update:       git pull && $DOCKER_COMPOSE build --no-cache && $DOCKER_COMPOSE up -d"
echo ""
echo "📚 For detailed documentation, see DEPLOYMENT.md"
echo ""

# Show current status
echo "📊 Current Status:"
$DOCKER_COMPOSE ps

echo ""
echo "Happy chatting! 🤖✨"
