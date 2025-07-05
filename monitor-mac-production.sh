#!/bin/bash

# GPUStack UI Production Monitoring Script for Mac Studio Ultra 3

echo "🍎 GPUStack UI Production Monitoring"
echo "===================================="

# Check if containers are running
echo "📊 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "💾 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo ""
echo "🔍 Health Checks:"
echo "Backend Health:"
curl -s -k https://localhost/api/health | jq . 2>/dev/null || echo "❌ Backend health check failed"

echo ""
echo "📋 Recent Logs (last 10 lines):"
echo "Backend:"
docker logs gpustack-ui-backend-mac-prod --tail 10 2>/dev/null || echo "❌ Backend container not found"

echo ""
echo "Nginx:"
docker logs gpustack-ui-nginx-mac-prod --tail 10 2>/dev/null || echo "❌ Nginx container not found"

echo ""
echo "Redis:"
docker logs gpustack-ui-redis-mac-prod --tail 5 2>/dev/null || echo "❌ Redis container not found"

echo ""
echo "🌐 Network Status:"
echo "Port 80 (HTTP): $(lsof -i :80 > /dev/null 2>&1 && echo "✅ Open" || echo "❌ Closed")"
echo "Port 443 (HTTPS): $(lsof -i :443 > /dev/null 2>&1 && echo "✅ Open" || echo "❌ Closed")"
echo "Port 8001 (Backend): $(lsof -i :8001 > /dev/null 2>&1 && echo "✅ Open" || echo "❌ Closed")"

echo ""
echo "💻 System Resources:"
echo "CPU Usage: $(top -l 1 | grep "CPU usage" | awk '{print $3}')"
echo "Memory Usage: $(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//') pages free"
echo "Disk Usage: $(df -h / | tail -1 | awk '{print $5}')"

echo ""
echo "🔗 Access URLs:"
echo "Frontend: https://localhost"
echo "API Docs: https://localhost/docs"
echo "Health: https://localhost/health"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000"

echo ""
echo "📋 Quick Commands:"
echo "View logs: docker logs -f gpustack-ui-backend-mac-prod"
echo "Restart: docker-compose -f docker-compose.mac-prod.yml restart"
echo "Stop: docker-compose -f docker-compose.mac-prod.yml down"
echo "Update: ./deploy-mac-production.sh" 