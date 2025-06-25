# GPUStack UI Frontend Configuration

This document explains how to configure the frontend to connect to your GPUStack backend server.

## Backend URL Configuration

The frontend uses a configurable backend URL system that allows you to easily point to different GPUStack backend servers without rebuilding the application.

### Configuration Files

- **`public/config.js`** - Main configuration file that sets the backend URL
- **`.env.local`** - Environment variables for Next.js (if needed)
- **`configure-backend.sh`** - Helper script to update the backend URL

### Quick Configuration

#### Method 1: Using the Helper Script (Recommended)

```bash
# Configure for local development
./configure-backend.sh http://localhost:8001

# Configure for remote server (replace with your server's IP/domain)
./configure-backend.sh http://192.168.1.231:8001

# Configure for production domain
./configure-backend.sh https://your-gpustack-server.com:8001
```

#### Method 2: Manual Configuration

Edit `public/config.js` directly:

```javascript
window.CONFIG = {
    BACKEND_URL: 'http://YOUR_SERVER_IP:8001'  // Replace with your backend URL
};
```

### Common Configuration Examples

#### Local Development
```bash
./configure-backend.sh http://localhost:8001
```

#### Remote Server on LAN
```bash
./configure-backend.sh http://192.168.1.231:8001
```

#### Remote Server with Domain
```bash
./configure-backend.sh https://ai-server.yourcompany.com:8001
```

#### Docker Deployment
If running in Docker, you might need to use the Docker host IP:
```bash
./configure-backend.sh http://host.docker.internal:8001
```

### Troubleshooting

#### "Backend Disconnected" Error

1. **Check the backend URL**: Make sure the URL in `config.js` matches your GPUStack server
2. **Verify backend is running**: Ensure your GPUStack backend is running on the specified port
3. **Check network access**: Make sure the frontend can reach the backend (no firewall blocking)
4. **CORS issues**: Ensure the backend allows connections from the frontend domain

#### Testing Backend Connection

You can test if the backend is accessible by visiting the URL directly in your browser:
```
http://YOUR_BACKEND_URL/
```

You should see a JSON response like:
```json
{"message": "GPUStack API is running"}
```

### Development vs Production

#### Development
- No rebuild needed after changing configuration
- Just refresh the browser after updating `config.js`
- Use `npm run dev` to start development server

#### Production
- After changing configuration, rebuild with `npm run build`
- Use `npm run start` to serve the production build
- Consider using environment variables for different deployment targets

### Environment Variables (Alternative Method)

You can also use Next.js environment variables by setting `NEXT_PUBLIC_BACKEND_URL`:

```bash
# In .env.local
NEXT_PUBLIC_BACKEND_URL=http://192.168.1.231:8001
```

Then rebuild the application:
```bash
npm run build
npm run start
```

### Docker Configuration

If running the frontend in Docker, you can:

1. **Use build-time configuration**:
   ```dockerfile
   ARG BACKEND_URL=http://localhost:8001
   RUN ./configure-backend.sh $BACKEND_URL
   ```

2. **Use runtime configuration**:
   Mount a custom `config.js` file as a volume:
   ```bash
   docker run -v ./custom-config.js:/app/public/config.js gpustack-ui
   ```

### Security Considerations

- Always use HTTPS in production environments
- Ensure the backend has proper CORS configuration
- Consider using authentication if exposing publicly
- Validate that the backend URL is accessible from the client's network
