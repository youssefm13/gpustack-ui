#!/bin/bash

# GPUStack UI Monitoring Startup Script
# This script starts Prometheus and Grafana for monitoring

set -e

echo "🚀 Starting GPUStack UI Monitoring Stack..."

# Check if docker-compose.mac-prod.yml exists
if [ ! -f "docker-compose.mac-prod.yml" ]; then
    echo "❌ Error: docker-compose.mac-prod.yml not found!"
    echo "Please ensure you're in the correct directory."
    exit 1
fi

# Check if monitoring directory exists
if [ ! -d "monitoring" ]; then
    echo "❌ Error: monitoring directory not found!"
    echo "Please ensure the monitoring configuration is set up."
    exit 1
fi

# Start monitoring services
echo "📊 Starting Prometheus and Grafana..."
docker-compose -f docker-compose.mac-prod.yml up -d prometheus grafana

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker-compose -f docker-compose.mac-prod.yml ps prometheus grafana

# Test Prometheus endpoint
echo "🧪 Testing Prometheus endpoint..."
if curl -s http://localhost:9090/api/v1/targets > /dev/null; then
    echo "✅ Prometheus is running at http://localhost:9090"
else
    echo "⚠️  Prometheus might still be starting up..."
fi

# Test Grafana endpoint
echo "🧪 Testing Grafana endpoint..."
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Grafana is running at http://localhost:3000"
else
    echo "⚠️  Grafana might still be starting up..."
fi

# Test backend metrics endpoint
echo "🧪 Testing backend metrics endpoint..."
if curl -s http://localhost:8001/api/prometheus > /dev/null; then
    echo "✅ Backend metrics endpoint is accessible"
else
    echo "⚠️  Backend metrics endpoint might not be available"
    echo "   Make sure your backend is running: docker-compose -f docker-compose.mac-prod.yml up -d backend"
fi

echo ""
echo "🎉 Monitoring stack started successfully!"
echo ""
echo "📊 Access your monitoring dashboards:"
echo "   • Grafana: http://localhost:3000 (admin/admin)"
echo "   • Prometheus: http://localhost:9090"
echo ""
echo "📋 Useful commands:"
echo "   • View logs: docker-compose -f docker-compose.mac-prod.yml logs prometheus grafana"
echo "   • Stop monitoring: docker-compose -f docker-compose.mac-prod.yml stop prometheus grafana"
echo "   • Restart monitoring: docker-compose -f docker-compose.mac-prod.yml restart prometheus grafana"
echo ""
echo "📖 For detailed monitoring guide, see: MONITORING_GUIDE.md" 