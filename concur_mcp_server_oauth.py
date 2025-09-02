#!/usr/bin/env python3
"""
Concur MCP Server with OAuth Authentication
Enhanced version with OAuth support using fastmcp-oauth
"""

import os
import sys
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables from .env if present
load_dotenv()

# Initialize the MCP server
mcp = FastMCP(name="ConcurReportServerOAuth")

# Try to import OAuth support (optional dependency)
try:
    from fastmcp_oauth import MicrosoftOAuth, GoogleOAuth, require_auth
    OAUTH_AVAILABLE = True
    print("✅ OAuth support available")
except ImportError:
    OAUTH_AVAILABLE = False
    print("⚠️  OAuth support not available. Install with: pip install git+https://github.com/peterlarnholt/fastmcp-oauth.git")
    
    # Create a dummy decorator for when OAuth is not available
    def require_auth(func):
        return func

# Configure OAuth if available
if OAUTH_AVAILABLE:
    # You can choose between different OAuth providers
    oauth_provider = os.getenv("OAUTH_PROVIDER", "microsoft")  # or "google"
    
    if oauth_provider == "microsoft":
        try:
            oauth = MicrosoftOAuth.from_env()
            app = oauth.install(mcp)
            print("✅ Microsoft OAuth configured")
        except Exception as e:
            print(f"⚠️  Microsoft OAuth setup failed: {e}")
            OAUTH_AVAILABLE = False
    elif oauth_provider == "google":
        try:
            oauth = GoogleOAuth.from_env()
            app = oauth.install(mcp)
            print("✅ Google OAuth configured")
        except Exception as e:
            print(f"⚠️  Google OAuth setup failed: {e}")
            OAUTH_AVAILABLE = False

# Concur API configuration
client_id = os.getenv("CONCUR_CLIENT_ID")
client_secret = os.getenv("CONCUR_CLIENT_SECRET")

def missing_vars():
    """Check for missing required environment variables."""
    return [
        var for var, val in [
            ("CONCUR_CLIENT_ID", client_id),
            ("CONCUR_CLIENT_SECRET", client_secret),
        ] if not val
    ]

def get_access_token_oauth(user_token: str = None) -> str:
    """
    Get an access token from Concur using OAuth2 authorization code flow.
    This would typically use the user's OAuth token to get a Concur-specific token.
    """
    # In a real implementation, you would:
    # 1. Use the user's OAuth token to identify them
    # 2. Either use their stored Concur credentials or 
    # 3. Redirect them to Concur's OAuth flow
    
    # For now, fall back to client credentials if available
    username = os.getenv("CONCUR_USERNAME")
    password = os.getenv("CONCUR_PASSWORD")
    
    if not username or not password:
        raise ValueError("Concur username/password not available. In production, implement proper OAuth flow.")
    
    # Concur OAuth2 token endpoint (US instance)
    TOKEN_URL = "https://integration.api.concursolutions.com/oauth2/v0/token"
    
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "password",
        "username": username,
        "password": password,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(TOKEN_URL, data=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["access_token"]
    except requests.RequestException as e:
        error_msg = f"Error requesting token: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f"\nResponse: {e.response.text}"
        raise Exception(error_msg)

@mcp.tool
@require_auth  # This decorator requires OAuth authentication
def list_concur_reports_protected(ctx, limit: int = 25) -> Dict[str, Any]:
    """
    List Concur expense reports for the authenticated user (OAuth protected).
    
    Args:
        limit: Maximum number of reports to return (default: 25, max: 100)
    
    Returns:
        Dictionary containing the list of reports and metadata
    """
    try:
        # Get user info from OAuth context
        user_info = ""
        if OAUTH_AVAILABLE and hasattr(ctx, 'auth') and ctx.auth.user:
            user_info = f" for user {ctx.auth.user.name} ({ctx.auth.user.email})"
        
        # Get access token (in production, this would use the user's OAuth token)
        access_token = get_access_token_oauth()
        
        # Concur API endpoint for expense reports (v3)
        reports_url = "https://integration.api.concursolutions.com/api/v3.0/expense/reports"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Add limit parameter
        params = {
            "limit": min(max(1, limit), 100)  # Ensure limit is between 1 and 100
        }
        
        response = requests.get(reports_url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract and format the reports data
        reports = data.get('Items', [])
        
        # Format the response with useful information
        formatted_reports = []
        for report in reports:
            formatted_report = {
                'id': report.get('ID'),
                'name': report.get('Name'),
                'purpose': report.get('Purpose'),
                'total': report.get('Total'),
                'currency_code': report.get('CurrencyCode'),
                'submission_date': report.get('SubmitDate'),
                'approval_status': report.get('ApprovalStatusName'),
                'workflow_step': report.get('WorkflowStepName'),
                'owner_name': report.get('OwnerName'),
                'created_date': report.get('CreateDate'),
                'last_modified_date': report.get('LastModifiedDate')
            }
            formatted_reports.append(formatted_report)
        
        return {
            'success': True,
            'count': len(formatted_reports),
            'reports': formatted_reports,
            'total_available': data.get('TotalCount', len(formatted_reports)),
            'message': f"Successfully retrieved {len(formatted_reports)} expense reports{user_info}",
            'authenticated_user': user_info.strip() if user_info else "OAuth not available"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to retrieve Concur reports: {str(e)}"
        }

@mcp.tool
def list_concur_reports_public(limit: int = 25) -> Dict[str, Any]:
    """
    List Concur expense reports (public access - no OAuth required).
    This is the same as the original function for backwards compatibility.
    
    Args:
        limit: Maximum number of reports to return (default: 25, max: 100)
    
    Returns:
        Dictionary containing the list of reports and metadata
    """
    try:
        # Use the original authentication method
        username = os.getenv("CONCUR_USERNAME")
        password = os.getenv("CONCUR_PASSWORD")
        
        if not username or not password:
            return {
                'success': False,
                'error': 'Missing credentials',
                'message': 'CONCUR_USERNAME and CONCUR_PASSWORD environment variables required'
            }
        
        access_token = get_access_token_oauth()  # This will use username/password
        
        # Same API call logic as the protected version
        reports_url = "https://integration.api.concursolutions.com/api/v3.0/expense/reports"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        params = {
            "limit": min(max(1, limit), 100)
        }
        
        response = requests.get(reports_url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        reports = data.get('Items', [])
        
        formatted_reports = []
        for report in reports:
            formatted_report = {
                'id': report.get('ID'),
                'name': report.get('Name'),
                'purpose': report.get('Purpose'),
                'total': report.get('Total'),
                'currency_code': report.get('CurrencyCode'),
                'submission_date': report.get('SubmitDate'),
                'approval_status': report.get('ApprovalStatusName'),
                'workflow_step': report.get('WorkflowStepName'),
                'owner_name': report.get('OwnerName'),
                'created_date': report.get('CreateDate'),
                'last_modified_date': report.get('LastModifiedDate')
            }
            formatted_reports.append(formatted_report)
        
        return {
            'success': True,
            'count': len(formatted_reports),
            'reports': formatted_reports,
            'total_available': data.get('TotalCount', len(formatted_reports)),
            'message': f"Successfully retrieved {len(formatted_reports)} expense reports (public access)"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to retrieve Concur reports: {str(e)}"
        }

@mcp.tool
@require_auth
def get_user_profile(ctx) -> Dict[str, Any]:
    """
    Get the authenticated user's profile information.
    This tool demonstrates OAuth authentication.
    
    Returns:
        Dictionary containing user profile information
    """
    if not OAUTH_AVAILABLE:
        return {
            'success': False,
            'error': 'OAuth not available',
            'message': 'OAuth support not installed'
        }
    
    if not hasattr(ctx, 'auth') or not ctx.auth.user:
        return {
            'success': False,
            'error': 'No user authenticated',
            'message': 'User authentication required'
        }
    
    user = ctx.auth.user
    return {
        'success': True,
        'user': {
            'name': user.name,
            'email': user.email,
            'id': getattr(user, 'id', 'N/A'),
        },
        'message': f"Successfully retrieved profile for {user.name}"
    }

@mcp.tool
def test_oauth_status() -> Dict[str, Any]:
    """
    Test OAuth configuration status.
    
    Returns:
        Dictionary indicating OAuth availability and configuration
    """
    return {
        'oauth_available': OAUTH_AVAILABLE,
        'oauth_provider': os.getenv("OAUTH_PROVIDER", "not_set"),
        'required_env_vars': [
            "SECRET_KEY",
            "MICROSOFT_CLIENT_ID" if os.getenv("OAUTH_PROVIDER") == "microsoft" else "GOOGLE_CLIENT_ID",
            "MICROSOFT_CLIENT_SECRET" if os.getenv("OAUTH_PROVIDER") == "microsoft" else "GOOGLE_CLIENT_SECRET",
        ],
        'message': 'OAuth is ready' if OAUTH_AVAILABLE else 'OAuth not configured'
    }

if __name__ == "__main__":
    # Check for required environment variables before starting
    if missing_vars():
        print(f"Error: Missing required Concur environment variables: {', '.join(missing_vars())}")
        print("Please set these variables in your .env file or environment.")
        sys.exit(1)
    
    print("Starting Concur MCP Server with OAuth support...")
    print("Available tools:")
    if OAUTH_AVAILABLE:
        print("  OAuth Protected:")
        print("    - list_concur_reports_protected: List expense reports (requires OAuth)")
        print("    - get_user_profile: Get authenticated user profile")
    print("  Public Access:")
    print("    - list_concur_reports_public: List expense reports (no OAuth)")
    print("    - test_oauth_status: Check OAuth configuration")
    
    if OAUTH_AVAILABLE:
        print(f"\n🔐 OAuth Provider: {os.getenv('OAUTH_PROVIDER', 'not_set')}")
        print("🌐 OAuth authentication will be required for protected tools")
    else:
        print("\n⚠️  OAuth not configured - only public tools available")
    
    # Run the MCP server
    mcp.run()
