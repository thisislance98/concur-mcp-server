# OAuth Setup Guide for Concur MCP Server

This guide explains how to add OAuth authentication to your Concur MCP Server using FastMCP OAuth.

## 🔐 **OAuth Features**

Your server now supports **both OAuth-protected and public tools**:

### **OAuth-Protected Tools** (require authentication):
- `list_concur_reports_protected` - List expense reports with user context
- `get_user_profile` - Get authenticated user's profile information

### **Public Tools** (no authentication required):
- `list_concur_reports_public` - List expense reports (backwards compatible)
- `test_oauth_status` - Check OAuth configuration status

## 🚀 **Setup Instructions**

### **Step 1: Install OAuth Support**
```bash
pip install git+https://github.com/peterlarnholt/fastmcp-oauth.git
```

### **Step 2: Choose OAuth Provider**

#### **Option A: Microsoft OAuth (Azure/Entra ID)**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **App registrations** > **New registration**
3. Set redirect URI to: `http://localhost:8000/oauth/callback`
4. Get your **Client ID** and **Client Secret**

#### **Option B: Google OAuth**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Set redirect URI to: `http://localhost:8000/oauth/callback`

### **Step 3: Configure Environment Variables**

Add these to your `.env` file:

#### **For Microsoft OAuth:**
```env
# OAuth Configuration
OAUTH_PROVIDER=microsoft
SECRET_KEY=your-super-secret-key-must-be-at-least-32-characters-long
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_TENANT=common  # or your specific tenant ID

# Existing Concur credentials
CONCUR_CLIENT_ID=your_concur_client_id
CONCUR_CLIENT_SECRET=your_concur_client_secret
CONCUR_USERNAME=your_concur_username
CONCUR_PASSWORD=your_concur_password
```

#### **For Google OAuth:**
```env
# OAuth Configuration
OAUTH_PROVIDER=google
SECRET_KEY=your-super-secret-key-must-be-at-least-32-characters-long
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Existing Concur credentials
CONCUR_CLIENT_ID=your_concur_client_id
CONCUR_CLIENT_SECRET=your_concur_client_secret
CONCUR_USERNAME=your_concur_username
CONCUR_PASSWORD=your_concur_password
```

## 🧪 **Testing OAuth**

### **Test 1: Check OAuth Status**
```bash
python test_oauth_server.py
```

### **Test 2: Start OAuth-Enabled Server**
```bash
python concur_mcp_server_oauth.py
```

### **Test 3: Use MCP Client with OAuth**
```python
from fastmcp import Client

async def test_with_oauth():
    # Connect to OAuth-enabled server
    async with Client("http://localhost:8000/mcp/", auth="oauth") as client:
        # This will open a browser for OAuth authentication
        result = await client.call_tool("list_concur_reports_protected", {"limit": 5})
        print(result)
```

## 🔄 **How OAuth Works**

1. **User requests protected tool** → Server redirects to OAuth provider
2. **User authenticates** with Microsoft/Google → Gets authorization code
3. **Server exchanges code for token** → Validates user identity
4. **Protected tools receive user context** → Access user-specific data

## 🛡️ **Security Benefits**

- **No hardcoded passwords** in environment variables
- **User-specific access** to Concur data
- **Token-based authentication** with expiration
- **Secure redirect flow** with PKCE protection
- **Multi-user support** - different users can authenticate

## 🔧 **Architecture**

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   MCP       │    │    OAuth     │    │   Concur    │
│   Client    │◄──►│   FastMCP    │◄──►│    API      │
│             │    │   Server     │    │             │
└─────────────┘    └──────────────┘    └─────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │   OAuth      │
                   │   Provider   │
                   │ (MS/Google)  │
                   └──────────────┘
```

## 🚦 **Current Status**

✅ **OAuth package installed**  
✅ **Server supports both OAuth and public access**  
✅ **Graceful fallback when OAuth not configured**  
⚠️  **OAuth credentials not configured** (add to `.env`)  
⚠️  **Protected tools require OAuth setup**  

## 📝 **Next Steps**

1. **Choose OAuth provider** (Microsoft or Google)
2. **Register your application** with the provider
3. **Add OAuth credentials** to `.env` file
4. **Test OAuth authentication** with a browser
5. **Deploy with OAuth support** for production use

## 💡 **Production Considerations**

- Use **HTTPS** in production (required for OAuth)
- Store secrets in **secure environment variables**
- Configure **proper redirect URIs** for your domain
- Consider **token refresh** for long-running sessions
- Implement **user session management** if needed

Your MCP server is now OAuth-ready! 🎉
