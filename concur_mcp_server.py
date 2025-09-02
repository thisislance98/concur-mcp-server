#!/usr/bin/env python3
"""
Concur MCP Server using FastMCP
A Model Context Protocol server that provides tools to interact with Concur expense reports.
Uses the ConcurExpenseSDK for all API interactions.
"""

import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv
from fastmcp import FastMCP
from concur_expense_sdk import ConcurExpenseSDK, AuthenticationError, NotFoundError, ValidationError, ConcurAPIError
from concur_expense_tools import create_expense_tools

# Load environment variables from .env if present
load_dotenv()

# Initialize the MCP server
mcp = FastMCP(name="ConcurReportServer")

# Initialize the Concur SDK
try:
    concur_sdk = ConcurExpenseSDK()
except AuthenticationError as e:
    print(f"Authentication error: {e}")
    sys.exit(1)

# Add expense-related tools
create_expense_tools(mcp, concur_sdk)

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
        result = concur_sdk.list_reports(limit=limit)
        if result['success']:
            result['message'] = f"Successfully retrieved {result['count']} expense reports"
        return result
        
    except (AuthenticationError, NotFoundError, ValidationError, ConcurAPIError) as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to retrieve Concur reports: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Unexpected error retrieving Concur reports: {str(e)}"
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
        result = concur_sdk.get_report(report_id)
        if result['success']:
            result['message'] = f"Successfully retrieved details for report {report_id}"
        return result
        
    except NotFoundError:
        return {
            'success': False,
            'error': 'Report not found',
            'message': f"No report found with ID: {report_id}"
        }
    except (AuthenticationError, ValidationError, ConcurAPIError) as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to retrieve report details: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Unexpected error retrieving report details: {str(e)}"
        }

@mcp.tool
def test_concur_connection() -> Dict[str, Any]:
    """
    Test the connection to Concur by attempting to authenticate.
    
    Returns:
        Dictionary indicating whether the connection was successful
    """
    return concur_sdk.test_connection()

@mcp.tool
def create_concur_report(name: str, purpose: str = "", business_purpose: str = "", 
                        currency_code: str = "USD", country: str = "US") -> Dict[str, Any]:
    """
    Create a new Concur expense report.
    
    Args:
        name: Report name
        purpose: Report purpose (optional)
        business_purpose: Business purpose (optional)
        currency_code: Currency code (default: USD)
        country: Country code (default: US)
    
    Returns:
        Dictionary containing created report details
    """
    try:
        result = concur_sdk.create_report(
            name=name, 
            purpose=purpose, 
            business_purpose=business_purpose,
            currency_code=currency_code, 
            country=country
        )
        return result
        
    except (AuthenticationError, ValidationError, ConcurAPIError) as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to create report: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Unexpected error creating report: {str(e)}"
        }

@mcp.tool
def update_concur_report(report_id: str, name: str = None, purpose: str = None, 
                        business_purpose: str = None, currency_code: str = None, 
                        country: str = None) -> Dict[str, Any]:
    """
    Update an existing Concur expense report.
    
    Args:
        report_id: The ID of the report to update
        name: New report name (optional)
        purpose: New report purpose (optional)
        business_purpose: New business purpose (optional)
        currency_code: New currency code (optional)
        country: New country code (optional)
    
    Returns:
        Dictionary indicating success/failure
    """
    try:
        # Build kwargs with only non-None values
        kwargs = {}
        if name is not None:
            kwargs['name'] = name
        if purpose is not None:
            kwargs['purpose'] = purpose
        if business_purpose is not None:
            kwargs['business_purpose'] = business_purpose
        if currency_code is not None:
            kwargs['currency_code'] = currency_code
        if country is not None:
            kwargs['country'] = country
        
        if not kwargs:
            return {
                'success': False,
                'error': 'No fields to update',
                'message': 'At least one field must be provided for update'
            }
        
        result = concur_sdk.update_report(report_id, **kwargs)
        return result
        
    except NotFoundError:
        return {
            'success': False,
            'error': 'Report not found',
            'message': f"No report found with ID: {report_id}"
        }
    except (AuthenticationError, ValidationError, ConcurAPIError) as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to update report: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Unexpected error updating report: {str(e)}"
        }

@mcp.tool
def delete_concur_report(report_id: str) -> Dict[str, Any]:
    """
    Delete a Concur expense report.
    
    Args:
        report_id: The ID of the report to delete
    
    Returns:
        Dictionary indicating success/failure
    """
    try:
        result = concur_sdk.delete_report(report_id)
        return result
        
    except NotFoundError:
        return {
            'success': False,
            'error': 'Report not found',
            'message': f"No report found with ID: {report_id}"
        }
    except (AuthenticationError, ValidationError, ConcurAPIError) as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to delete report: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Unexpected error deleting report: {str(e)}"
        }

if __name__ == "__main__":
    print("Starting Concur MCP Server...")
    print("Available tools:")
    print("  Report Management:")
    print("    - list_concur_reports: List expense reports")
    print("    - get_concur_report_details: Get detailed info for a specific report")
    print("    - create_concur_report: Create a new expense report")
    print("    - update_concur_report: Update an existing report")
    print("    - delete_concur_report: Delete a report")
    print("  Expense Management:")
    print("    - list_concur_expenses: List expenses in a report")
    print("    - get_concur_expense_details: Get detailed info for a specific expense")
    print("    - create_concur_expense: Create a new expense entry")
    print("    - update_concur_expense: Update an existing expense")
    print("    - delete_concur_expense: Delete an expense entry")
    print("  Utility:")
    print("    - get_concur_expense_types: Get available expense types")
    print("    - get_concur_payment_types: Get available payment types")
    print("    - test_concur_connection: Test API connection")
    
    # Run the MCP server
    mcp.run()
