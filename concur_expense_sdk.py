#!/usr/bin/env python3
"""
Concur Expense SDK
A comprehensive SDK for interacting with Concur's expense management APIs.
Supports reports, expenses, expense entries, and related operations.
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConcurAPIError(Exception):
    """Base exception for Concur API errors."""
    pass


class AuthenticationError(ConcurAPIError):
    """Raised when authentication fails."""
    pass


class NotFoundError(ConcurAPIError):
    """Raised when a resource is not found."""
    pass


class ValidationError(ConcurAPIError):
    """Raised when request validation fails."""
    pass


class ReportStatus(Enum):
    """Expense report status enumeration."""
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    PAID = "Paid"
    REJECTED = "Rejected"


class ExpenseType(Enum):
    """Common expense types."""
    AIRFARE = "AIRFR"
    HOTEL = "LODNG"
    MEALS = "MEALS"
    CAR_RENTAL = "CARRT"
    TAXI = "TAXIC"
    PARKING = "PARKN"
    PHONE = "PHONE"
    INTERNET = "INTRN"
    OTHER = "OTHER"


@dataclass
class ConcurConfig:
    """Configuration for Concur API connection."""
    client_id: str
    client_secret: str
    username: str
    password: str
    base_url: str = "https://integration.api.concursolutions.com"
    token_url: str = "https://integration.api.concursolutions.com/oauth2/v0/token"
    api_version: str = "v4"  # Updated to use v4 endpoints


@dataclass
class ExpenseReport:
    """Represents an expense report."""
    id: Optional[str] = None
    name: Optional[str] = None
    purpose: Optional[str] = None
    business_purpose: Optional[str] = None
    total: Optional[float] = None
    currency_code: Optional[str] = None
    submission_date: Optional[str] = None
    approval_status: Optional[str] = None
    workflow_step: Optional[str] = None
    owner_name: Optional[str] = None
    created_date: Optional[str] = None
    last_modified_date: Optional[str] = None
    country: Optional[str] = None
    policy_id: Optional[str] = None
    report_version: Optional[int] = None


@dataclass
class ExpenseEntry:
    """Represents an expense entry within a report."""
    id: Optional[str] = None
    report_id: Optional[str] = None
    expense_type: Optional[str] = None
    transaction_amount: Optional[float] = None
    transaction_currency_code: Optional[str] = None
    transaction_date: Optional[str] = None
    business_purpose: Optional[str] = None
    vendor_description: Optional[str] = None
    city_name: Optional[str] = None
    country_code: Optional[str] = None
    payment_type: Optional[str] = None
    receipt_required: Optional[bool] = None
    has_receipt: Optional[bool] = None


class ConcurExpenseSDK:
    """
    Main SDK class for interacting with Concur Expense APIs.
    Provides methods for managing reports, expenses, and related operations.
    """

    def __init__(self, config: Optional[ConcurConfig] = None):
        """
        Initialize the Concur Expense SDK.
        
        Args:
            config: ConcurConfig object or None to load from environment variables
        """
        if config:
            self.config = config
        else:
            self.config = self._load_config_from_env()
        
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self.session = requests.Session()

    def _load_config_from_env(self) -> ConcurConfig:
        """Load configuration from environment variables."""
        required_vars = {
            'client_id': 'CONCUR_CLIENT_ID',
            'client_secret': 'CONCUR_CLIENT_SECRET',
            'username': 'CONCUR_USERNAME',
            'password': 'CONCUR_PASSWORD'
        }
        
        config_values = {}
        missing_vars = []
        
        for key, env_var in required_vars.items():
            value = os.getenv(env_var)
            if not value:
                missing_vars.append(env_var)
            config_values[key] = value
        
        if missing_vars:
            raise AuthenticationError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return ConcurConfig(**config_values)

    def _get_access_token(self) -> str:
        """Get or refresh the access token."""
        if self._access_token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._access_token
        
        payload = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "password",
            "username": self.config.username,
            "password": self.config.password,
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        try:
            response = self.session.post(self.config.token_url, data=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            self._access_token = data["access_token"]
            # Assume token expires in 1 hour if not specified
            expires_in = data.get("expires_in", 3600)
            from datetime import timedelta
            self._token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Successfully obtained access token")
            return self._access_token
            
        except requests.RequestException as e:
            error_msg = f"Error requesting token: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nResponse: {e.response.text}"
            raise AuthenticationError(error_msg)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an authenticated request to the Concur API."""
        access_token = self._get_access_token()
        
        headers = kwargs.pop('headers', {})
        headers.update({
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        
        # Use direct v4 endpoints like the notebook
        url = f"{self.config.base_url}/{endpoint}"
        
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response
            
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                # Token might be expired, clear it and retry once
                self._access_token = None
                access_token = self._get_access_token()
                headers["Authorization"] = f"Bearer {access_token}"
                response = self.session.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response
            elif e.response.status_code == 404:
                raise NotFoundError(f"Resource not found: {e.response.text}")
            elif e.response.status_code == 400:
                raise ValidationError(f"Bad request: {e.response.text}")
            else:
                raise ConcurAPIError(f"API error {e.response.status_code}: {e.response.text}")
        except requests.RequestException as e:
            raise ConcurAPIError(f"Request failed: {e}")

    # REPORT METHODS
    
    def list_reports(self, limit: int = 25, user: Optional[str] = None) -> Dict[str, Any]:
        """
        List expense reports.
        
        Args:
            limit: Maximum number of reports to return (1-100)
            user: User ID to filter reports (optional)
            
        Returns:
            Dictionary containing reports and metadata
        """
        # Get user ID if not provided
        if not user:
            user = self.get_user_id()
            if not user:
                raise AuthenticationError("Could not determine user ID")
        
        # Use v4 endpoint like the notebook
        endpoint = f"expensereports/v4/users/{user}/context/TRAVELER/reports"
        response = self._make_request("GET", endpoint)
        data = response.json()
        
        reports = []
        for item in data.get('content', []):
            report = ExpenseReport(
                id=item.get('reportId'),
                name=item.get('name'),
                purpose=item.get('purpose'),
                business_purpose=item.get('businessPurpose'),
                total=item.get('approvedAmount', {}).get('value') if item.get('approvedAmount') else None,
                currency_code=item.get('approvedAmount', {}).get('currencyCode') if item.get('approvedAmount') else None,
                submission_date=item.get('reportDate'),
                approval_status=item.get('approvalStatus'),
                workflow_step=item.get('workflowStep'),
                owner_name=item.get('ownerName'),
                created_date=item.get('creationDate'),
                last_modified_date=item.get('lastModifiedDate'),
                country=item.get('country'),
                policy_id=item.get('policyId'),
                report_version=item.get('reportVersion')
            )
            reports.append(asdict(report))
        
        return {
            'success': True,
            'reports': reports,
            'count': len(reports),
            'content': data.get('content', []),  # Keep original v4 format too
            'totalElements': data.get('totalElements'),
            'totalPages': data.get('totalPages')
        }


    def create_report(self, name: str, purpose: str = "", business_purpose: str = "", 
                     currency_code: str = "USD", country: str = "US") -> Dict[str, Any]:
        """
        Create a new expense report.
        
        Args:
            name: Report name
            purpose: Report purpose
            business_purpose: Business purpose
            currency_code: Currency code (default: USD)
            country: Country code (default: US)
            
        Returns:
            Dictionary containing created report details
        """
        # Get user ID for v4 endpoint
        user_id = self.get_user_id()
        if not user_id:
            raise AuthenticationError("Could not determine user ID")
        
        # Use v4 payload format like the notebook
        v4_payload = {
            "name": name,
            "reportDate": datetime.now().strftime('%Y-%m-%d'),
            "businessPurpose": business_purpose or purpose,
        }
        
        # Use v4 endpoint like the notebook
        endpoint = f"expensereports/v4/users/{user_id}/context/TRAVELER/reports"
        response = self._make_request("POST", endpoint, json=v4_payload)
        data = response.json()
        
        # Extract report ID from URI like the notebook
        report_id = None
        if 'uri' in data:
            report_id = data['uri'].split('/')[-1]
        
        return {
            'success': True,
            'report_id': report_id,
            'uri': data.get('uri'),
            'ID': report_id,  # For compatibility
            'message': f"Successfully created report: {name}"
        }


    def delete_report(self, report_id: str) -> Dict[str, Any]:
        """
        Delete an expense report using v4 endpoint (like notebook).
        
        Args:
            report_id: The ID of the report to delete
            
        Returns:
            Dictionary indicating success/failure
        """
        # Get user ID for v4 endpoint
        user_id = self.get_user_id()
        if not user_id:
            raise AuthenticationError("Could not determine user ID")
        
        # Use v4 endpoint like the notebook
        endpoint = f"expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}"
        response = self._make_request("DELETE", endpoint)
        
        return {
            'success': True,
            'message': f"Successfully deleted report {report_id}",
            'api_version': 'v4'
        }

    # EXPENSE ENTRY METHODS
    
    def list_expenses(self, report_id: str, limit: int = 25, offset: int = 0) -> Dict[str, Any]:
        """
        List expense entries for a specific report using v4 endpoint.
        
        Args:
            report_id: The ID of the report
            limit: Maximum number of expenses to return (1-100)
            offset: Number of records to skip
            
        Returns:
            Dictionary containing expenses and metadata
        """
        # Get user ID for v4 endpoint
        user_id = self.get_user_id()
        if not user_id:
            raise AuthenticationError("Could not determine user ID")
        
        # Use v4 endpoint like the notebook
        endpoint = f"expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses"
        response = self._make_request("GET", endpoint)
        data = response.json()
        
        expenses = []
        # Handle both v4 (array) and legacy formats
        items = data if isinstance(data, list) else data.get('Items', [])
        
        for item in items:
            # Try v4 format first, fall back to v3 format
            expense = ExpenseEntry(
                id=item.get('expenseId') or item.get('ID'),
                report_id=report_id,
                expense_type=(item.get('expenseType', {}).get('name') if item.get('expenseType') 
                             else item.get('ExpenseTypeName')),
                transaction_amount=(item.get('transactionAmount', {}).get('value') if item.get('transactionAmount') 
                                  else item.get('TransactionAmount')),
                transaction_currency_code=(item.get('transactionAmount', {}).get('currencyCode') if item.get('transactionAmount') 
                                         else item.get('TransactionCurrencyCode')),
                transaction_date=item.get('transactionDate') or item.get('TransactionDate'),
                business_purpose=(item.get('businessPurpose', {}).get('value') if item.get('businessPurpose') 
                                else item.get('BusinessPurpose')),
                vendor_description=(item.get('vendor', {}).get('description') if item.get('vendor') 
                                  else item.get('VendorDescription')),
                city_name=(item.get('location', {}).get('city') if item.get('location') 
                          else item.get('LocationName')),
                country_code=(item.get('location', {}).get('countryCode') if item.get('location') 
                            else item.get('CountryCode')),
                payment_type=(item.get('paymentType', {}).get('name') if item.get('paymentType') 
                            else item.get('PaymentTypeName')),
                receipt_required=item.get('receiptRequired') or item.get('ReceiptRequired'),
                has_receipt=item.get('hasReceipt') or item.get('HasReceipt')
            )
            expenses.append(asdict(expense))
        
        return {
            'success': True,
            'expenses': expenses,
            'count': len(expenses),
            'api_version': 'v4',
            'report_id': report_id,
            'message': f'Retrieved {len(expenses)} expenses from report {report_id}'
        }


    def create_expense(self, report_id: str, expense_type: str, amount: float, 
                      currency_code: str = "USD", transaction_date: Optional[str] = None,
                      business_purpose: str = "", vendor_description: str = "",
                      city_name: str = "", country_code: str = "US",
                      payment_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new expense entry in a report using v4 endpoint.
        
        Args:
            report_id: The ID of the report to add the expense to
            expense_type: Type of expense (expense type ID from get_expense_types)
            amount: Transaction amount
            currency_code: Currency code (default: USD)
            transaction_date: Date of transaction in YYYY-MM-DD format (default: today)
            business_purpose: Business purpose of the expense
            vendor_description: Vendor/merchant description
            city_name: City where expense occurred
            country_code: Country code (default: US)
            payment_type: Payment method name (optional)
            
        Returns:
            Dictionary containing created expense details
        """
        if transaction_date is None:
            transaction_date = date.today().strftime("%Y-%m-%d")
        
        # Get user ID for v4 endpoint
        user_id = self.get_user_id()
        if not user_id:
            raise AuthenticationError("Could not determine user ID")
        
        # Get the expense type name for the payload
        expense_type_name = expense_type  # Default to ID
        
        # Try to get the actual name from get_expense_types if possible
        try:
            expense_types_result = self.get_expense_types()
            if expense_types_result['success']:
                for et in expense_types_result['expense_types']:
                    if et['id'] == expense_type:
                        expense_type_name = et['name']
                        break
        except:
            pass  # Use ID as name if lookup fails
        
        # Build v4 payload - try simpler structure based on error analysis
        payload = {
            "expenseSource": "EA",
            "exchangeRate": {
                "value": 1,
                "operation": "MULTIPLY"
            },
            "expenseType": {
                "id": expense_type,
                "name": expense_type_name,
                "isDeleted": False,
                "listItemId": None
            },
            "transactionAmount": {
                "value": amount,
                "currencyCode": currency_code.lower()
            },
            "transactionDate": transaction_date
        }
        
        # Add vendor as object with description field
        if vendor_description and vendor_description.strip():
            payload["vendor"] = {
                "description": vendor_description
            }
        
        # Add business purpose - try as simple string first
        if business_purpose and business_purpose.strip():
            payload["businessPurpose"] = business_purpose
        
        try:
            # Use v4 endpoint like the notebook
            endpoint = f"expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses"
            response = self._make_request("POST", endpoint, json=payload)
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'expense_id': None,  # v4 doesn't return ID in response
                    'message': f"Successfully created expense entry for {amount} {currency_code}",
                    'api_version': 'v4',
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'message': f"Failed to create expense entry: HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to create expense entry: {str(e)}"
            }

    def update_expense(self, expense_id: str, report_id: str, amount: Optional[float] = None, 
                      expense_type_id: Optional[str] = None, expense_type_name: Optional[str] = None,
                      date: Optional[str] = None, vendor: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing expense entry using v4 endpoint (like notebook).
        
        Args:
            expense_id: The ID of the expense to update
            report_id: The ID of the report containing the expense
            amount: Updated transaction amount
            expense_type_id: Updated expense type ID
            expense_type_name: Updated expense type name
            date: Updated transaction date
            vendor: Updated vendor description
            
        Returns:
            Dictionary indicating success/failure
        """
        # Get user ID for v4 endpoint
        user_id = self.get_user_id()
        if not user_id:
            raise AuthenticationError("Could not determine user ID")
        
        # Build v4 payload like the notebook
        payload = {
            "expenseSource": "EA",
            "exchangeRate": {
                "value": 1,
                "operation": "MULTIPLY"
            }
        }
        
        # Only add fields that are provided (like the notebook)
        if expense_type_id and expense_type_name:
            payload["expenseType"] = {
                "id": expense_type_id,
                "name": expense_type_name,
                "isDeleted": False,
                "listItemId": None
            }
        
        if amount:
            payload["transactionAmount"] = {
                "value": amount,
                "currencyCode": "usd"
            }
        
        if vendor:
            payload["vendor"] = {
                "description": vendor
            }
            
        if date:
            payload["transactionDate"] = date
        
        try:
            # Use v4 endpoint with PATCH like the notebook
            endpoint = f"expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses/{expense_id}"
            response = self._make_request("PATCH", endpoint, json=payload)
            
            if response.status_code in [200, 201, 204]:  # 204 No Content is success for PATCH
                return {
                    'success': True,
                    'message': f"Successfully updated expense {expense_id}",
                    'api_version': 'v4',
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'message': f"Failed to update expense: HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to update expense: {str(e)}"
            }

    def delete_expense(self, expense_id: str, report_id: str) -> Dict[str, Any]:
        """
        Delete an expense entry using v4 endpoint (like notebook).
        
        Args:
            expense_id: The ID of the expense to delete
            report_id: The ID of the report containing the expense
            
        Returns:
            Dictionary indicating success/failure
        """
        # Get user ID for v4 endpoint
        user_id = self.get_user_id()
        if not user_id:
            raise AuthenticationError("Could not determine user ID")
        
        # Use v4 endpoint like the notebook
        endpoint = f"expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses/{expense_id}"
        response = self._make_request("DELETE", endpoint)
        
        return {
            'success': True,
            'message': f"Successfully deleted expense {expense_id} from report {report_id}",
            'api_version': 'v4'
        }


    # UTILITY METHODS
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to Concur API.
        
        Returns:
            Dictionary indicating connection status
        """
        try:
            access_token = self._get_access_token()
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

    def get_user_id(self) -> Optional[str]:
        """Get the current user ID from the profile endpoint."""
        try:
            # Use the profile URL from the JWT token
            access_token = self._get_access_token()
            # Decode JWT to get profile URL
            import json
            import base64
            
            parts = access_token.split('.')
            payload = parts[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            payload_decoded = json.loads(base64.urlsafe_b64decode(payload))
            
            profile_url = payload_decoded.get('concur.profile')
            if profile_url:
                # Extract user ID from profile URL
                user_id = profile_url.split('/')[-1]
                return user_id
            
            return None
        except Exception as e:
            logger.error(f"Failed to get user ID: {e}")
            return None

    def get_expense_types(self) -> Dict[str, Any]:
        """
        Get available expense types using user-specific v4 endpoint (like notebook).
        
        Returns:
            Dictionary containing expense types for the specific user
        """
        try:
            # Get user ID for user-specific endpoint
            user_id = self.get_user_id()
            if not user_id:
                raise AuthenticationError("Could not determine user ID")
            
            # Use user-specific expense types endpoint like the notebook
            endpoint = f"expenseconfig/v4/users/{user_id}/context/TRAVELER/expensetypes"
            response = self._make_request("GET", endpoint)
            data = response.json()
            
            expense_types = []
            for item in data:
                # Filter out items that start with '0' like the notebook
                if not item.get('expenseTypeId', '').startswith('0'):
                    expense_types.append({
                        'name': item.get('name'),
                        'id': item.get('expenseTypeId'),
                        'code': item.get('expenseCategoryCode'),
                        'expense_type_id': item.get('expenseTypeId'),  # For compatibility
                        'description': item.get('description'),
                        'is_deleted': item.get('isDeleted', False)
                    })
            
            return {
                'success': True,
                'expense_types': expense_types,
                'Items': expense_types,  # For compatibility with old format
                'count': len(expense_types),
                'api_version': 'v4_user_specific',
                'message': f'Retrieved {len(expense_types)} expense types from user-specific configuration'
            }
                
        except Exception as e:
            # Final fallback: Try v3 API (though it usually fails with 403)
            try:
                logger.info(f"v4 APIs failed: {e}, trying v3 API fallback")
                response = self._make_request("GET", "expense/expensetypes")
                data = response.json()
                
                expense_types = []
                for item in data.get('Items', []):
                    expense_types.append({
                        'code': item.get('Code'),
                        'name': item.get('Name'),
                        'category': item.get('CategoryCode'),
                        'spend_category': None,
                        'expense_type_id': item.get('ID'),
                        'description': None,
                        'is_deleted': False,
                        'show_on_mobile': True
                    })
                
                return {
                    'success': True,
                    'expense_types': expense_types,
                    'count': len(expense_types),
                    'api_version': 'v3',
                    'message': f'Retrieved {len(expense_types)} expense types from v3 API'
                }
            except Exception as v3_error:
                return {
                    'success': False,
                    'error': str(e),
                    'fallback_error': str(v3_error),
                    'message': f'Failed to retrieve expense types from all APIs: v4_user_policy, v4_company ({e}) and v3 ({v3_error})'
                }

    def get_payment_types(self) -> Dict[str, Any]:
        """
        Get available payment types using v4 API.
        
        Returns:
            Dictionary containing payment types
        """
        try:
            # Try v3 API first
            try:
                response = self._make_request("GET", "expense/paymenttypes")
                data = response.json()
                
                payment_types = []
                for item in data.get('Items', []):
                    payment_types.append({
                        'code': item.get('Code'),
                        'name': item.get('Name'),
                        'id': item.get('ID')
                    })
                
                return {
                    'success': True,
                    'payment_types': payment_types,
                    'count': len(payment_types)
                }
            except Exception as v3_error:
                logger.info(f"v3 API failed: {v3_error}, trying v4 API")
                
                # Try v4 API with user ID
                user_id = self.get_user_id()
                if not user_id:
                    raise Exception("Could not get user ID for v4 API")
                
                # Use v4 endpoint
                url = f"{self.config.base_url}/expenseconfig/v4/users/{user_id}/paymenttypes"
                headers = {
                    "Authorization": f"Bearer {self._get_access_token()}",
                    "Accept": "application/json"
                }
                
                response = self.session.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                payment_types = []
                # Handle both list and dict responses
                items = data if isinstance(data, list) else data.get('content', data.get('items', []))
                
                for item in items:
                    payment_types.append({
                        'code': item.get('paymentTypeId'),  # v4 uses paymentTypeId
                        'name': item.get('paymentTypeName'),  # v4 uses paymentTypeName
                        'id': item.get('paymentTypeId'),  # Use paymentTypeId as both code and id
                        'is_default': item.get('isDefault', False)
                    })
                
                return {
                    'success': True,
                    'payment_types': payment_types,
                    'count': len(payment_types),
                    'api_version': 'v4'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve payment types: {str(e)}'
            }
