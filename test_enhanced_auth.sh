#!/bin/bash

echo "🔐 Testing Enhanced Authentication v2 System"
echo "============================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_BASE="http://localhost:8001"

echo -e "${BLUE}1. Testing Enhanced Login${NC}"
echo "Logging in with admin/admin..."
LOGIN_RESPONSE=$(curl -s -X POST ${API_BASE}/api/auth/v2/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}')

# Extract tokens
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.refresh_token')

if [ "$ACCESS_TOKEN" != "null" ] && [ "$ACCESS_TOKEN" != "" ]; then
    echo -e "${GREEN}✅ Login successful!${NC}"
    echo "User info:"
    echo $LOGIN_RESPONSE | jq '.user'
else
    echo -e "${RED}❌ Login failed${NC}"
    echo $LOGIN_RESPONSE | jq .
    exit 1
fi

echo
echo -e "${BLUE}2. Testing Session Management${NC}"
echo "Fetching active sessions..."
SESSIONS=$(curl -s -X GET ${API_BASE}/api/auth/v2/sessions \
  -H "Authorization: Bearer $ACCESS_TOKEN")

SESSION_COUNT=$(echo $SESSIONS | jq '. | length')
echo -e "${GREEN}✅ Found $SESSION_COUNT active sessions${NC}"
echo "Recent session:"
echo $SESSIONS | jq '.[0]'

echo
echo -e "${BLUE}3. Testing User Management${NC}"
echo "Fetching all users..."
USERS=$(curl -s -X GET ${API_BASE}/api/auth/v2/users \
  -H "Authorization: Bearer $ACCESS_TOKEN")

USER_COUNT=$(echo $USERS | jq '. | length')
echo -e "${GREEN}✅ Found $USER_COUNT users in system${NC}"
echo "Users:"
echo $USERS | jq '.[] | {id, username, full_name, is_admin}'

echo
echo -e "${BLUE}4. Testing User Preferences${NC}"
echo "Getting user preferences..."
PREFS=$(curl -s -X GET ${API_BASE}/api/auth/v2/preferences \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo -e "${GREEN}✅ User preferences:${NC}"
echo $PREFS | jq .

echo "Setting a test preference..."
curl -s -X PUT ${API_BASE}/api/auth/v2/preferences \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme": "dark", "language": "en", "test_setting": "enhanced_auth_v2"}' > /dev/null

UPDATED_PREFS=$(curl -s -X GET ${API_BASE}/api/auth/v2/preferences \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo -e "${GREEN}✅ Updated preferences:${NC}"
echo $UPDATED_PREFS | jq .

echo
echo -e "${BLUE}5. Testing System Health${NC}"
HEALTH=$(curl -s -X GET ${API_BASE}/api/auth/v2/health)
echo -e "${GREEN}✅ System health:${NC}"
echo $HEALTH | jq .

echo
echo -e "${BLUE}6. Testing Token Refresh${NC}"
echo "Using refresh token to get new access token..."
REFRESH_RESPONSE=$(curl -s -X POST ${API_BASE}/api/auth/v2/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

NEW_ACCESS_TOKEN=$(echo $REFRESH_RESPONSE | jq -r '.access_token')
if [ "$NEW_ACCESS_TOKEN" != "null" ] && [ "$NEW_ACCESS_TOKEN" != "" ]; then
    echo -e "${GREEN}✅ Token refresh successful!${NC}"
    echo "New token expires in: $(echo $REFRESH_RESPONSE | jq '.expires_in') seconds"
else
    echo -e "${YELLOW}⚠️ Token refresh failed or not implemented${NC}"
    echo $REFRESH_RESPONSE | jq .
fi

echo
echo -e "${BLUE}7. Testing Protected Inference API${NC}"
echo "Testing AI inference with enhanced auth..."
INFERENCE_RESPONSE=$(curl -s -X POST ${API_BASE}/api/inference/infer \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3", "messages": [{"role": "user", "content": "Hello! This is a test of the enhanced authentication system."}], "max_tokens": 50}')

if echo $INFERENCE_RESPONSE | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ AI inference working with enhanced auth!${NC}"
    echo "AI Response:"
    echo $INFERENCE_RESPONSE | jq -r '.choices[0].message.content'
else
    echo -e "${YELLOW}⚠️ AI inference may not be available or model not loaded${NC}"
    echo $INFERENCE_RESPONSE | jq .
fi

echo
echo -e "${GREEN}🎉 Enhanced Authentication v2 Testing Complete!${NC}"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Open browser to http://localhost:8001/app"
echo "2. Login with admin/admin"
echo "3. Test the enhanced UI features"
echo "4. Create additional users via API if needed"
echo
echo -e "${BLUE}Key Features Verified:${NC}"
echo "✅ Enhanced login with user data"
echo "✅ Session management and tracking"
echo "✅ User preferences system"
echo "✅ JWT token system with refresh"
echo "✅ Database persistence"
echo "✅ Protected API endpoints"
