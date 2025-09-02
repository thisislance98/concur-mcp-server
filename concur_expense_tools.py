#!/usr/bin/env python3
"""
Additional Concur MCP Tools for Expense Management
Provides tools for managing individual expense entries within reports.
"""

from typing import Dict, Any
from concur_expense_sdk import ConcurExpenseSDK, AuthenticationError, NotFoundError, ValidationError, ConcurAPIError

def create_expense_tools(mcp, concur_sdk: ConcurExpenseSDK):
    """Add expense-related tools to the MCP server."""
    
    @mcp.tool
    def list_concur_expenses(report_id: str, limit: int = 25, offset: int = 0) -> Dict[str, Any]:
        """
        List expense entries for a specific Concur report.
        
        Args:
            report_id: The ID of the report
            limit: Maximum number of expenses to return (default: 25, max: 100)
            offset: Number of records to skip (default: 0)
        
        Returns:
            Dictionary containing expenses and metadata
        """
        try:
            result = concur_sdk.list_expenses(report_id=report_id, limit=limit, offset=offset)
            if result['success']:
                result['message'] = f"Successfully retrieved {result['count']} expenses for report {report_id}"
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
                'message': f"Failed to retrieve expenses: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Unexpected error retrieving expenses: {str(e)}"
            }

    @mcp.tool
    def get_concur_expense_details(expense_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific expense entry.
        
        Args:
            expense_id: The ID of the expense entry to retrieve
        
        Returns:
            Dictionary containing expense details
        """
        try:
            result = concur_sdk.get_expense(expense_id)
            if result['success']:
                result['message'] = f"Successfully retrieved details for expense {expense_id}"
            return result
            
        except NotFoundError:
            return {
                'success': False,
                'error': 'Expense not found',
                'message': f"No expense found with ID: {expense_id}"
            }
        except (AuthenticationError, ValidationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to retrieve expense details: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Unexpected error retrieving expense details: {str(e)}"
            }

    @mcp.tool
    def create_concur_expense(report_id: str, expense_type: str, amount: float, 
                             currency_code: str = "USD", transaction_date: str = None,
                             business_purpose: str = "", vendor_description: str = "",
                             city_name: str = "", country_code: str = "US",
                             payment_type: str = "CASH") -> Dict[str, Any]:
        """
        Create a new expense entry in a report.
        
        Args:
            report_id: The ID of the report to add the expense to
            expense_type: Type of expense (e.g., AIRFR, LODNG, MEALS, CARRT, TAXIC, PARKN, PHONE, INTRN, OTHER)
            amount: Transaction amount
            currency_code: Currency code (default: USD)
            transaction_date: Date of transaction in YYYY-MM-DD format (default: today)
            business_purpose: Business purpose of the expense
            vendor_description: Vendor/merchant description
            city_name: City where expense occurred
            country_code: Country code (default: US)
            payment_type: Payment method (default: CASH)
        
        Returns:
            Dictionary containing created expense details
        """
        try:
            result = concur_sdk.create_expense(
                report_id=report_id,
                expense_type=expense_type,
                amount=amount,
                currency_code=currency_code,
                transaction_date=transaction_date,
                business_purpose=business_purpose,
                vendor_description=vendor_description,
                city_name=city_name,
                country_code=country_code,
                payment_type=payment_type
            )
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
                'message': f"Failed to create expense: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Unexpected error creating expense: {str(e)}"
            }

    @mcp.tool
    def update_concur_expense(expense_id: str, amount: float = None, currency_code: str = None,
                             transaction_date: str = None, business_purpose: str = None,
                             vendor_description: str = None, city_name: str = None,
                             country_code: str = None, payment_type: str = None,
                             expense_type: str = None) -> Dict[str, Any]:
        """
        Update an existing expense entry.
        
        Args:
            expense_id: The ID of the expense entry to update
            amount: New transaction amount (optional)
            currency_code: New currency code (optional)
            transaction_date: New transaction date in YYYY-MM-DD format (optional)
            business_purpose: New business purpose (optional)
            vendor_description: New vendor description (optional)
            city_name: New city name (optional)
            country_code: New country code (optional)
            payment_type: New payment type (optional)
            expense_type: New expense type (optional)
        
        Returns:
            Dictionary indicating success/failure
        """
        try:
            # Build kwargs with only non-None values
            kwargs = {}
            if amount is not None:
                kwargs['amount'] = amount
            if currency_code is not None:
                kwargs['currency_code'] = currency_code
            if transaction_date is not None:
                kwargs['transaction_date'] = transaction_date
            if business_purpose is not None:
                kwargs['business_purpose'] = business_purpose
            if vendor_description is not None:
                kwargs['vendor_description'] = vendor_description
            if city_name is not None:
                kwargs['city_name'] = city_name
            if country_code is not None:
                kwargs['country_code'] = country_code
            if payment_type is not None:
                kwargs['payment_type'] = payment_type
            if expense_type is not None:
                kwargs['expense_type'] = expense_type
            
            if not kwargs:
                return {
                    'success': False,
                    'error': 'No fields to update',
                    'message': 'At least one field must be provided for update'
                }
            
            result = concur_sdk.update_expense(expense_id, **kwargs)
            return result
            
        except NotFoundError:
            return {
                'success': False,
                'error': 'Expense not found',
                'message': f"No expense found with ID: {expense_id}"
            }
        except (AuthenticationError, ValidationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to update expense: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Unexpected error updating expense: {str(e)}"
            }

    @mcp.tool
    def delete_concur_expense(expense_id: str) -> Dict[str, Any]:
        """
        Delete an expense entry.
        
        Args:
            expense_id: The ID of the expense entry to delete
        
        Returns:
            Dictionary indicating success/failure
        """
        try:
            result = concur_sdk.delete_expense(expense_id)
            return result
            
        except NotFoundError:
            return {
                'success': False,
                'error': 'Expense not found',
                'message': f"No expense found with ID: {expense_id}"
            }
        except (AuthenticationError, ValidationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to delete expense: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Unexpected error deleting expense: {str(e)}"
            }

    @mcp.tool
    def get_concur_expense_types() -> Dict[str, Any]:
        """
        Get available expense types from Concur.
        
        Returns:
            Dictionary containing expense types
        """
        try:
            result = concur_sdk.get_expense_types()
            return result
            
        except (AuthenticationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to retrieve expense types: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Unexpected error retrieving expense types: {str(e)}"
            }

    @mcp.tool
    def get_concur_payment_types() -> Dict[str, Any]:
        """
        Get available payment types from Concur.
        
        Returns:
            Dictionary containing payment types
        """
        try:
            result = concur_sdk.get_payment_types()
            return result
            
        except (AuthenticationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to retrieve payment types: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Unexpected error retrieving payment types: {str(e)}"
            }
