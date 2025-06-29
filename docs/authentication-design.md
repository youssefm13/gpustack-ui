# GPUStack UI Authentication System Design

## Overview
This document outlines the authentication system for GPUStack UI that integrates with GPUStack's user management while following security best practices.

## Architecture Options

### Option 1: GPUStack Integration (Recommended)
- **Pros**: Single sign-on experience, centralized user management, leverages existing GPUStack permissions
- **Cons**: Dependent on GPUStack API availability, potential complexity in token management

### Option 2: Standalone Authentication
- **Pros**: Independent operation, full control over auth flow, can work offline
- **Cons**: Duplicate user management, potential sync issues

## Recommended Implementation: Hybrid Approach

### Core Components

1. **Authentication Service** (`backend/services/auth_service.py`)
   - Handle login/logout
   - Token validation and refresh
   - User session management
   - GPUStack API integration

2. **User Models** (`backend/models/user.py`)
   - User data structures
   - Permission levels
   - Session management

3. **Middleware** (`backend/middleware/auth.py`)
   - Request authentication
   - Route protection
   - CORS handling

4. **Frontend Auth** (`frontend/src/auth/`)
   - Login/logout UI
   - Token storage (secure)
   - Protected route handling

### Authentication Flow

#### Login Process
1. User enters credentials in UI
2. Frontend sends credentials to our backend `/api/auth/login`
3. Backend validates credentials against GPUStack `/v1/users`
4. If valid, backend generates JWT token with user info
5. Frontend stores token securely and redirects to main app

#### Request Authentication
1. Frontend includes JWT token in Authorization header
2. Backend middleware validates token
3. Extracts user context for request processing
4. Continues to protected endpoint

#### Token Management
- **Access tokens**: Short-lived (15-30 minutes)
- **Refresh tokens**: Longer-lived (7 days)
- **Automatic refresh**: Background token renewal

### Security Features

1. **JWT Tokens**: Stateless, secure, configurable expiration
2. **Password Hashing**: bcrypt or Argon2 for local storage
3. **HTTPS Enforcement**: All auth endpoints require HTTPS in production
4. **Rate Limiting**: Prevent brute force attacks
5. **CORS Configuration**: Secure cross-origin requests
6. **Session Management**: Proper logout and token invalidation

### User Roles and Permissions

Based on GPUStack user structure:
- **Admin**: Full access to all features, user management
- **User**: Standard access to inference, file upload, search
- **Guest**: Limited access (if enabled)

### Configuration

Environment variables:
```bash
# Authentication settings
AUTH_MODE=gpustack  # or standalone
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# GPUStack integration
GPUSTACK_API_URL=http://your-gpustack/v1
GPUSTACK_API_KEY=your-api-key

# Security settings
REQUIRE_HTTPS=true
ENABLE_GUEST_ACCESS=false
MAX_LOGIN_ATTEMPTS=5
LOGIN_ATTEMPT_WINDOW_MINUTES=15
```

### Database Schema (Optional)

For standalone mode or enhanced features:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(100),
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    gpustack_id INTEGER,  -- Link to GPUStack user
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    token_jti VARCHAR(255) UNIQUE,  -- JWT ID for blacklisting
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/me` - Current user info

#### User Management (Admin only)
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Frontend Components

1. **Login Page** (`/login`)
   - Username/password form
   - Remember me option
   - Forgot password link

2. **Protected Routes**
   - Automatic redirect to login
   - User context provider
   - Permission-based rendering

3. **User Menu**
   - Profile management
   - Logout option
   - Admin panel (for admins)

### Implementation Phases

#### Phase 1: Basic Authentication
- JWT-based login/logout
- GPUStack user validation
- Protected routes
- Basic user context

#### Phase 2: Enhanced Security
- Token refresh mechanism
- Rate limiting
- Session management
- Password policies

#### Phase 3: Advanced Features
- User management UI
- Role-based permissions
- Audit logging
- SSO integration (optional)

### Testing Strategy

1. **Unit Tests**: Auth service functions, token validation
2. **Integration Tests**: GPUStack API interaction, database operations
3. **Security Tests**: Token manipulation, injection attacks
4. **E2E Tests**: Complete login/logout flows, protected routes

### Deployment Considerations

1. **Environment Setup**: Secure secret management
2. **HTTPS**: SSL certificates for production
3. **Database**: Migration scripts for user tables
4. **Monitoring**: Authentication metrics and alerts
