#!/usr/bin/env python3
"""
Robust Concur MCP Server
Enhanced version with better error handling and deployment compatibility
"""

import os
import sys
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check and validate environment variables"""
    logger.info("Checking environment configuration...")
    
    # Load environment variables with fallbacks
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("✅ Environment variables loaded from .env")
    except ImportError:
        logger.warning("⚠️  python-dotenv not available, using system environment only")
    except Exception as e:
        logger.warning(f"⚠️  Could not load .env file: {e}")
    
    # Required environment variables
    required_vars = {
        "CONCUR_CLIENT_ID": os.getenv("CONCUR_CLIENT_ID"),
        "CONCUR_CLIENT_SECRET": os.getenv("CONCUR_CLIENT_SECRET"), 
        "CONCUR_USERNAME": os.getenv("CONCUR_USERNAME"),
        "CONCUR_PASSWORD": os.getenv("CONCUR_PASSWORD")
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your deployment environment:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        return False
    
    # Log success (without exposing values)
    for var in required_vars:
        logger.info(f"✅ {var}: configured")
    
    return True

def safe_import():
    """Safely import all required modules with detailed error reporting"""
    logger.info("Importing required modules...")
    
    try:
        from fastmcp import FastMCP
        logger.info("✅ FastMCP imported")
    except ImportError as e:
        logger.error(f"❌ FastMCP import failed: {e}")
        logger.error("Install with: pip install fastmcp>=2.11.3")
        return False
    
    try:
        from concur_expense_sdk import ConcurExpenseSDK, AuthenticationError, NotFoundError, ValidationError, ConcurAPIError
        logger.info("✅ ConcurExpenseSDK imported")
    except ImportError as e:
        logger.error(f"❌ ConcurExpenseSDK import failed: {e}")
        logger.error("Ensure concur_expense_sdk.py is in the same directory")
        return False
    
    try:
        from concur_expense_tools import create_expense_tools
        logger.info("✅ concur_expense_tools imported")
    except ImportError as e:
        logger.error(f"❌ concur_expense_tools import failed: {e}")
        logger.error("Ensure concur_expense_tools.py is in the same directory")
        return False
    
    return True

def initialize_server():
    """Initialize the MCP server with comprehensive error handling"""
    logger.info("Initializing MCP server...")
    
    try:
        from fastmcp import FastMCP
        from concur_expense_sdk import ConcurExpenseSDK, AuthenticationError, NotFoundError, ValidationError, ConcurAPIError
        from concur_expense_tools import create_expense_tools
        
        # Initialize the MCP server
        mcp = FastMCP(name="ConcurReportServer")
        logger.info("✅ FastMCP server created")
        
        # Initialize the Concur SDK with error handling
        try:
            concur_sdk = ConcurExpenseSDK()
            logger.info("✅ ConcurExpenseSDK initialized")
            
            # Test connection
            connection_result = concur_sdk.test_connection()
            if connection_result.get('success'):
                logger.info("✅ Concur API connection verified")
            else:
                logger.warning(f"⚠️  Concur API connection test failed: {connection_result.get('message')}")
                
        except AuthenticationError as e:
            logger.error(f"❌ Concur authentication failed: {e}")
            logger.error("Check your CONCUR_USERNAME and CONCUR_PASSWORD")
            return None
        except Exception as e:
            logger.error(f"❌ SDK initialization failed: {e}")
            return None
        
        # Add expense-related tools
        try:
            create_expense_tools(mcp, concur_sdk)
            logger.info("✅ Expense tools registered")
        except Exception as e:
            logger.error(f"❌ Failed to register expense tools: {e}")
            return None
        
        # Add core report management tools
        @mcp.tool()
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
        
        @mcp.tool()
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
        
        @mcp.tool()
        def test_concur_connection() -> Dict[str, Any]:
            """
            Test the connection to Concur by attempting to authenticate.
            
            Returns:
                Dictionary indicating whether the connection was successful
            """
            return concur_sdk.test_connection()
        
        @mcp.tool()
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
        
        logger.info("✅ Core tools registered")
        
        # Log available tools
        tool_count = len([name for name in dir(mcp) if not name.startswith('_')])
        logger.info(f"✅ Server initialized with {tool_count} tools")
        
        return mcp
        
    except Exception as e:
        logger.error(f"❌ Server initialization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def main():
    """Main server startup function"""
    logger.info("🚀 Starting Concur MCP Server (Robust Version)")
    logger.info("=" * 60)
    
    # Step 1: Check environment
    if not check_environment():
        logger.error("❌ Environment check failed")
        return False
    
    # Step 2: Check imports
    if not safe_import():
        logger.error("❌ Import check failed")
        return False
    
    # Step 3: Initialize server
    mcp = initialize_server()
    if not mcp:
        logger.error("❌ Server initialization failed")
        return False
    
    # Step 4: Start server
    logger.info("🎯 Starting MCP server...")
    logger.info("Available tools:")
    logger.info("  Report Management:")
    logger.info("    - list_concur_reports: List expense reports")
    logger.info("    - get_concur_report_details: Get detailed info for a specific report")
    logger.info("    - create_concur_report: Create a new expense report")
    logger.info("  Expense Management:")
    logger.info("    - list_concur_expenses: List expenses in a report")
    logger.info("    - get_concur_expense_details: Get detailed info for a specific expense")
    logger.info("    - create_concur_expense: Create a new expense entry (defaults to INCTS)")
    logger.info("    - update_concur_expense: Update an existing expense")
    logger.info("    - delete_concur_expense: Delete an expense entry")
    logger.info("  Utility:")
    logger.info("    - get_concur_expense_types: Get available expense types")
    logger.info("    - get_concur_payment_types: Get available payment types")
    logger.info("    - test_concur_connection: Test API connection")
    logger.info("  Documentation:")
    logger.info("    - get_concur_api_guide: Get comprehensive API documentation and code examples")
    
    try:
        # Run the MCP server
        logger.info("✅ Server starting successfully...")
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
        return True
    except Exception as e:
        logger.error(f"❌ Server runtime error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
