#!/usr/bin/env python3
"""
Concur MCP Server using FastMCP
A Model Context Protocol server that provides tools to interact with Concur expense reports.
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
mcp = FastMCP(name="ConcurReportServer")

# Required environment variables
client_id = os.getenv("CONCUR_CLIENT_ID")
client_secret = os.getenv("CONCUR_CLIENT_SECRET")
username = os.getenv("CONCUR_USERNAME")
password = os.getenv("CONCUR_PASSWORD")

def missing_vars():
    """Check for missing required environment variables."""
    return [
        var for var, val in [
            ("CONCUR_CLIENT_ID", client_id),
            ("CONCUR_CLIENT_SECRET", client_secret),
            ("CONCUR_USERNAME", username),
            ("CONCUR_PASSWORD", password),
        ] if not val
    ]

def get_access_token() -> str:
    """Get an access token from Concur using OAuth2 password grant."""
    if missing_vars():
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars())}")
    
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
def list_concur_reports(limit: int = 25) -> Dict[str, Any]:
    """
    List Concur expense reports for the authenticated user.
    
    Args:
        limit: Maximum number of reports to return (default: 25, max: 100)
    
    Returns:
        Dictionary containing the list of reports and metadata
    """
    try:
        # Get access token
        access_token = get_access_token()
        
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
            'message': f"Successfully retrieved {len(formatted_reports)} expense reports"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to retrieve Concur reports: {str(e)}"
        }

@mcp.tool
def get_concur_report_details(report_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific Concur expense report.
    
    Args:
        report_id: The ID of the expense report to retrieve
    
    Returns:
        Dictionary containing detailed report information
    """
    try:
        # Get access token
        access_token = get_access_token()
        
        # Concur API endpoint for a specific expense report (v3)
        report_url = f"https://integration.api.concursolutions.com/api/v3.0/expense/reports/{report_id}"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.get(report_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Format the detailed report information
        report_details = {
            'id': data.get('ID'),
            'name': data.get('Name'),
            'purpose': data.get('Purpose'),
            'total': data.get('Total'),
            'currency_code': data.get('CurrencyCode'),
            'submission_date': data.get('SubmitDate'),
            'approval_status': data.get('ApprovalStatusName'),
            'workflow_step': data.get('WorkflowStepName'),
            'owner_name': data.get('OwnerName'),
            'created_date': data.get('CreateDate'),
            'last_modified_date': data.get('LastModifiedDate'),
            'business_purpose': data.get('BusinessPurpose'),
            'country': data.get('Country'),
            'expense_entries_uri': data.get('ExpenseEntriesURI'),
            'policy_id': data.get('PolicyID'),
            'report_version': data.get('ReportVersion')
        }
        
        return {
            'success': True,
            'report': report_details,
            'message': f"Successfully retrieved details for report {report_id}"
        }
        
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return {
                'success': False,
                'error': 'Report not found',
                'message': f"No report found with ID: {report_id}"
            }
        else:
            return {
                'success': False,
                'error': str(e),
                'message': f"HTTP error retrieving report {report_id}: {str(e)}"
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to retrieve report details: {str(e)}"
        }

@mcp.tool
def test_concur_connection() -> Dict[str, Any]:
    """
    Test the connection to Concur by attempting to authenticate.
    
    Returns:
        Dictionary indicating whether the connection was successful
    """
    try:
        access_token = get_access_token()
        return {
            'success': True,
            'message': 'Successfully connected to Concur API',
            'token_length': len(access_token),
            'token_prefix': access_token[:20] + '...' if len(access_token) > 20 else access_token
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Failed to connect to Concur API: {str(e)}'
        }

if __name__ == "__main__":
    # Check for required environment variables before starting
    if missing_vars():
        print(f"Error: Missing required environment variables: {', '.join(missing_vars())}")
        print("Please set these variables in your .env file or environment.")
        sys.exit(1)
    
    print("Starting Concur MCP Server...")
    print("Available tools:")
    print("  - list_concur_reports: List expense reports")
    print("  - get_concur_report_details: Get detailed info for a specific report")
    print("  - test_concur_connection: Test API connection")
    
    # Run the MCP server
    mcp.run()
