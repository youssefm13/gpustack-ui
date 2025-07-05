#!/bin/bash

# GPUStack UI Performance Optimization for Mac Studio Ultra 3
# Optimizes Docker and system settings for maximum performance

echo "🚀 GPUStack UI Performance Optimization for Mac Studio Ultra 3"
echo "============================================================="

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS"
    exit 1
fi

echo "🔧 Optimizing Docker Desktop settings..."

# Check current Docker Desktop settings
echo "Current Docker Desktop settings:"
echo "Memory: $(docker system info --format '{{.MemTotal}}' 2>/dev/null)"
echo "CPUs: $(docker system info --format '{{.NCPU}}' 2>/dev/null)"

echo ""
echo "📋 Recommended settings for Mac Studio Ultra 3:"
echo "Memory: 16-32GB (you have plenty!)"
echo "CPUs: 8-16 cores"
echo "Disk: 100GB+"
echo ""
echo "To configure:"
echo "1. Open Docker Desktop"
echo "2. Go to Settings → Resources"
echo "3. Set Memory to 16-32GB"
echo "4. Set CPUs to 8-16"
echo "5. Enable 'Use the new Virtualization framework'"
echo "6. Apply & Restart"

echo ""
echo "🔍 Checking system resources..."

# Check available memory
TOTAL_MEM=$(sysctl -n hw.memsize | awk '{print $0/1024/1024/1024}')
FREE_MEM=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
FREE_MEM_GB=$(echo "scale=2; $FREE_MEM * 4096 / 1024 / 1024 / 1024" | bc)

echo "Total Memory: ${TOTAL_MEM}GB"
echo "Available Memory: ${FREE_MEM_GB}GB"

# Check CPU cores
CPU_CORES=$(sysctl -n hw.ncpu)
echo "CPU Cores: $CPU_CORES"

# Optimize Docker settings
echo ""
echo "⚙️  Optimizing Docker settings..."

# Create optimized docker-compose override
cat > docker-compose.mac-optimized.yml << EOF
version: '3.8'

services:
  backend:
    environment:
      - WORKERS=8
      - PYTHONUNBUFFERED=1
      - PYTHONDONTWRITEBYTECODE=1
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'
    ulimits:
      nofile:
        soft: 65536
        hard: 65536

  redis:
    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  nginx:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
EOF

echo "✅ Created optimized Docker Compose configuration"

# Optimize system settings
echo ""
echo "🔧 Optimizing system settings..."

# Check if we can optimize network settings
if command -v sysctl > /dev/null 2>&1; then
    echo "Network optimizations:"
    echo "Current TCP keepalive: $(sysctl -n net.inet.tcp.keepalive_time 2>/dev/null || echo 'Not set')"
    echo "Current TCP connections: $(sysctl -n kern.ipc.somaxconn 2>/dev/null || echo 'Not set')"
fi

# Create performance monitoring script
cat > monitor-performance.sh << 'EOF'
#!/bin/bash

echo "📊 GPUStack UI Performance Monitor"
echo "=================================="

echo "🖥️  System Resources:"
echo "CPU Usage: $(top -l 1 | grep "CPU usage" | awk '{print $3}')"
echo "Memory Usage: $(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//') pages free"
echo "Disk Usage: $(df -h / | tail -1 | awk '{print $5}')"

echo ""
echo "🐳 Docker Resources:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo ""
echo "📈 Application Performance:"
echo "Response Time: $(curl -s -w "%{time_total}s" -o /dev/null https://localhost/api/health)"
echo "Active Connections: $(lsof -i :443 | wc -l | awk '{print $1-1}')"
EOF

chmod +x monitor-performance.sh

echo ""
echo "🎯 Performance Optimization Complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure Docker Desktop with recommended settings"
echo "2. Restart Docker Desktop"
echo "3. Run: ./deploy-mac-production.sh"
echo "4. Monitor performance: ./monitor-performance.sh"
echo ""
echo "💡 Tips for maximum performance:"
echo "- Close unnecessary applications"
echo "- Keep Docker Desktop running"
echo "- Monitor Activity Monitor for resource usage"
echo "- Use Safari for testing (better performance than Chrome)"
echo "" 