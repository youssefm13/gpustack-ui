# GPUStack UI Backend URL Fix

## Problem Summary
The GPUStack UI frontend had a hardcoded backend URL (`http://localhost:8001`) in the `index.html` file, which caused connectivity issues when accessing the UI from devices other than the one running the backend server. This resulted in "Backend Disconnected" status when accessing the UI externally.

## Solution Implemented

### 1. Configuration System
- **Created**: `frontend/public/config.js` - Centralized configuration file
- **Modified**: `frontend/public/index.html` - Updated to use configurable backend URL
- **Created**: `frontend/.env.local` - Environment variables for Next.js
- **Updated**: `frontend/next.config.js` - Added environment variable support

### 2. Helper Tools
- **Created**: `frontend/configure-backend.sh` - Easy configuration script
- **Created**: `frontend/README.md` - Comprehensive configuration guide

### 3. Changes Made

#### Before (Hardcoded):
```javascript
const API_BASE = 'http://localhost:8001';
```

#### After (Configurable):
```javascript
const API_BASE = window.CONFIG ? window.CONFIG.BACKEND_URL : 'http://localhost:8001';
```

### 4. Configuration Files Created

#### `frontend/public/config.js`
```javascript
window.CONFIG = {
    BACKEND_URL: 'http://192.168.1.231:8001'
};
```

#### `frontend/.env.local`
```
NEXT_PUBLIC_BACKEND_URL=http://192.168.1.231:8001
```

## How to Use

### Quick Fix (Immediate)
```bash
cd /Users/mahmoudyoussef/gpustack-ui/frontend
./configure-backend.sh http://192.168.1.231:8001
```

### Manual Configuration
Edit `frontend/public/config.js` and change the `BACKEND_URL` to your server's IP or domain.

### For Different Environments

#### Local Development
```bash
./configure-backend.sh http://localhost:8001
```

#### LAN Access (your current setup)
```bash
./configure-backend.sh http://192.168.1.231:8001
```

#### Public Domain
```bash
./configure-backend.sh https://your-domain.com:8001
```

## Benefits of This Solution

1. **No Rebuild Required**: Changes take effect immediately, just refresh the browser
2. **Environment Flexible**: Easy to switch between development, staging, and production
3. **Docker Friendly**: Can be configured at runtime or build time
4. **Backward Compatible**: Falls back to localhost if config is missing
5. **Easy to Deploy**: Configuration script makes it simple for different environments

## Testing the Fix

1. **Configure the backend URL**:
   ```bash
   cd frontend
   ./configure-backend.sh http://192.168.1.231:8001
   ```

2. **Access the UI from another device** on your network:
   ```
   http://192.168.1.231:3000  # or whatever port your frontend runs on
   ```

3. **Check connection status**: The UI should now show "Backend Connected" instead of "Backend Disconnected"

## File Structure
```
gpustack-ui/
├── frontend/
│   ├── public/
│   │   ├── config.js          # ✅ NEW: Configuration file
│   │   └── index.html         # ✅ MODIFIED: Uses configurable URL
│   ├── .env.local             # ✅ NEW: Environment variables
│   ├── next.config.js         # ✅ MODIFIED: Added env support
│   ├── configure-backend.sh   # ✅ NEW: Configuration script
│   └── README.md              # ✅ NEW: Configuration guide
├── .env                       # ✅ EXISTING: Contains backend URL
└── BACKEND_URL_FIX.md         # ✅ NEW: This summary
```

## Technical Details

The solution works by:
1. Loading a configuration object (`window.CONFIG`) before the main application script
2. Using JavaScript to check if the config exists and use its values
3. Falling back to localhost if no configuration is provided
4. Providing multiple ways to set the configuration (script, manual edit, environment variables)

This approach is framework-agnostic and works with static HTML files, making it perfect for this mixed Next.js/static HTML setup.

## Future Improvements

- Add validation for backend URL format
- Add automatic backend URL detection
- Add configuration UI within the application
- Add support for multiple backend environments
- Add configuration via URL parameters
