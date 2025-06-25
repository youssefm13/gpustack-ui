#!/bin/bash
# Configuration script for GPUStack UI Backend URL
# Usage: ./configure-backend.sh [BACKEND_URL]
# Example: ./configure-backend.sh http://192.168.1.231:8001

BACKEND_URL=${1:-"http://localhost:8001"}
CONFIG_FILE="./public/config.js"

echo "Configuring GPUStack UI backend URL to: $BACKEND_URL"

# Update the config.js file
cat > "$CONFIG_FILE" << EOF
// Configuration for the frontend application
// This can be modified during deployment to point to the correct backend
window.CONFIG = {
    // Change this URL to point to your GPUStack backend server
    // For local development: 'http://localhost:8001'
    // For remote access: 'http://YOUR_SERVER_IP:8001' or 'http://YOUR_DOMAIN:8001'
    BACKEND_URL: '$BACKEND_URL'
};
EOF

echo "✅ Backend URL updated in $CONFIG_FILE"
echo "Frontend will now connect to: $BACKEND_URL"
echo ""
echo "If you're running this in a Docker container or need to rebuild:"
echo "  - For development: No rebuild needed, just refresh the browser"
echo "  - For production builds: Run 'npm run build' to create optimized build"
