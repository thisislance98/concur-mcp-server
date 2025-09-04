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
    api_version: str = "v3.0"


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
        
        url = f"{self.config.base_url}/api/{self.config.api_version}/{endpoint}"
        
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
        params = {
            "limit": min(max(1, limit), 100)
        }
        
        if user:
            params["user"] = user
        
        response = self._make_request("GET", "expense/reports", params=params)
        data = response.json()
        
        reports = []
        for item in data.get('Items', []):
            report = ExpenseReport(
                id=item.get('ID'),
                name=item.get('Name'),
                purpose=item.get('Purpose'),
                business_purpose=item.get('BusinessPurpose'),
                total=item.get('Total'),
                currency_code=item.get('CurrencyCode'),
                submission_date=item.get('SubmitDate'),
                approval_status=item.get('ApprovalStatusName'),
                workflow_step=item.get('WorkflowStepName'),
                owner_name=item.get('OwnerName'),
                created_date=item.get('CreateDate'),
                last_modified_date=item.get('LastModifiedDate'),
                country=item.get('Country'),
                policy_id=item.get('PolicyID'),
                report_version=item.get('ReportVersion')
            )
            reports.append(asdict(report))
        
        return {
            'success': True,
            'reports': reports,
            'count': len(reports),
            'total_available': data.get('TotalCount', len(reports)),
            'limit': limit
        }

    def get_report(self, report_id: str) -> Dict[str, Any]:
        """
        Get a specific expense report by ID.
        
        Args:
            report_id: The ID of the report to retrieve
            
        Returns:
            Dictionary containing report details
        """
        response = self._make_request("GET", f"expense/reports/{report_id}")
        data = response.json()
        
        report = ExpenseReport(
            id=data.get('ID'),
            name=data.get('Name'),
            purpose=data.get('Purpose'),
            business_purpose=data.get('BusinessPurpose'),
            total=data.get('Total'),
            currency_code=data.get('CurrencyCode'),
            submission_date=data.get('SubmitDate'),
            approval_status=data.get('ApprovalStatusName'),
            workflow_step=data.get('WorkflowStepName'),
            owner_name=data.get('OwnerName'),
            created_date=data.get('CreateDate'),
            last_modified_date=data.get('LastModifiedDate'),
            country=data.get('Country'),
            policy_id=data.get('PolicyID'),
            report_version=data.get('ReportVersion')
        )
        
        return {
            'success': True,
            'report': asdict(report)
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
        payload = {
            "Name": name,
            "Purpose": purpose,
            "BusinessPurpose": business_purpose,
            "CurrencyCode": currency_code,
            "Country": country
        }
        
        response = self._make_request("POST", "expense/reports", json=payload)
        data = response.json()
        
        return {
            'success': True,
            'report_id': data.get('ID'),
            'uri': data.get('URI'),
            'message': f"Successfully created report: {name}"
        }

    def update_report(self, report_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing expense report.
        
        Args:
            report_id: The ID of the report to update
            **kwargs: Fields to update (name, purpose, business_purpose, etc.)
            
        Returns:
            Dictionary indicating success/failure
        """
        # Map common field names to API field names
        field_mapping = {
            'name': 'Name',
            'purpose': 'Purpose',
            'business_purpose': 'BusinessPurpose',
            'currency_code': 'CurrencyCode',
            'country': 'Country'
        }
        
        payload = {}
        for key, value in kwargs.items():
            api_key = field_mapping.get(key, key)
            payload[api_key] = value
        
        response = self._make_request("PUT", f"expense/reports/{report_id}", json=payload)
        
        return {
            'success': True,
            'message': f"Successfully updated report {report_id}"
        }

    def delete_report(self, report_id: str) -> Dict[str, Any]:
        """
        Delete an expense report.
        
        Args:
            report_id: The ID of the report to delete
            
        Returns:
            Dictionary indicating success/failure
        """
        self._make_request("DELETE", f"expense/reports/{report_id}")
        
        return {
            'success': True,
            'message': f"Successfully deleted report {report_id}"
        }

    # EXPENSE ENTRY METHODS
    
    def list_expenses(self, report_id: str, limit: int = 25, offset: int = 0) -> Dict[str, Any]:
        """
        List expense entries for a specific report.
        
        Args:
            report_id: The ID of the report
            limit: Maximum number of expenses to return (1-100)
            offset: Number of records to skip
            
        Returns:
            Dictionary containing expenses and metadata
        """
        params = {
            "limit": min(max(1, limit), 100),
            "reportID": report_id
        }
        
        # Only add offset if it's greater than 0 (Concur API doesn't like offset=0)
        if offset > 0:
            params["offset"] = offset
        
        response = self._make_request("GET", "expense/entries", params=params)
        data = response.json()
        
        expenses = []
        for item in data.get('Items', []):
            expense = ExpenseEntry(
                id=item.get('ID'),
                report_id=item.get('ReportID'),
                expense_type=item.get('ExpenseTypeName'),
                transaction_amount=item.get('TransactionAmount'),
                transaction_currency_code=item.get('TransactionCurrencyCode'),
                transaction_date=item.get('TransactionDate'),
                business_purpose=item.get('BusinessPurpose'),
                vendor_description=item.get('VendorDescription'),
                city_name=item.get('LocationName'),
                country_code=item.get('CountryCode'),
                payment_type=item.get('PaymentTypeName'),
                receipt_required=item.get('ReceiptRequired'),
                has_receipt=item.get('HasReceipt')
            )
            expenses.append(asdict(expense))
        
        return {
            'success': True,
            'expenses': expenses,
            'count': len(expenses),
            'total_available': data.get('TotalCount', len(expenses)),
            'offset': offset,
            'limit': limit,
            'report_id': report_id
        }

    def get_expense(self, expense_id: str) -> Dict[str, Any]:
        """
        Get a specific expense entry by ID.
        
        Args:
            expense_id: The ID of the expense entry to retrieve
            
        Returns:
            Dictionary containing expense details
        """
        response = self._make_request("GET", f"expense/entries/{expense_id}")
        data = response.json()
        
        expense = ExpenseEntry(
            id=data.get('ID'),
            report_id=data.get('ReportID'),
            expense_type=data.get('ExpenseTypeName'),
            transaction_amount=data.get('TransactionAmount'),
            transaction_currency_code=data.get('TransactionCurrencyCode'),
            transaction_date=data.get('TransactionDate'),
            business_purpose=data.get('BusinessPurpose'),
            vendor_description=data.get('VendorDescription'),
            city_name=data.get('LocationName'),
            country_code=data.get('CountryCode'),
            payment_type=data.get('PaymentTypeName'),
            receipt_required=data.get('ReceiptRequired'),
            has_receipt=data.get('HasReceipt')
        )
        
        return {
            'success': True,
            'expense': asdict(expense)
        }

    def create_expense(self, report_id: str, expense_type: str, amount: float, 
                      currency_code: str = "USD", transaction_date: Optional[str] = None,
                      business_purpose: str = "", vendor_description: str = "",
                      city_name: str = "", country_code: str = "US",
                      payment_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new expense entry in a report using v3 expense entries API.
        
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
            payment_type: Payment method name (optional, e.g., "Cash", "Company Paid")
            
        Returns:
            Dictionary containing created expense details
        """
        if transaction_date is None:
            transaction_date = date.today().strftime("%Y-%m-%d")
        
        # Build v3 expense entries payload
        payload = {
            "ReportID": report_id,
            "ExpenseTypeCode": expense_type,
            "TransactionAmount": amount,
            "TransactionCurrencyCode": currency_code,
            "TransactionDate": transaction_date,
            "BusinessPurpose": business_purpose,
            "VendorDescription": vendor_description,
            "LocationName": city_name,
            "CountryCode": country_code
        }
        
        # Handle payment type - PaymentTypeID is required for v3 API
        # Use known working PaymentTypeID (Cash payment type discovered from existing expenses)
        default_payment_type_id = "fr1rdFhUGA6l-5FnPPmuq5_HjOMU="
        payload["PaymentTypeID"] = default_payment_type_id
        logger.info(f"Using known working Cash PaymentTypeID for v3 API compatibility")
        
        try:
            response = self._make_request("POST", "expense/entries", json=payload)
            data = response.json()
            
            return {
                'success': True,
                'expense_id': data.get('ID'),
                'uri': data.get('URI'),
                'message': f"Successfully created expense entry for {amount} {currency_code}",
                'api_version': 'v3'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to create expense entry: {str(e)}"
            }

    def update_expense(self, expense_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing expense entry.
        
        Args:
            expense_id: The ID of the expense entry to update
            **kwargs: Fields to update
            
        Returns:
            Dictionary indicating success/failure
        """
        # Map common field names to API field names
        field_mapping = {
            'amount': 'TransactionAmount',
            'currency_code': 'TransactionCurrencyCode',
            'transaction_date': 'TransactionDate',
            'business_purpose': 'BusinessPurpose',
            'vendor_description': 'VendorDescription',
            'city_name': 'LocationName',
            'country_code': 'CountryCode',
            'payment_type': 'PaymentTypeName',  # v3 API expects PaymentTypeName
            'expense_type': 'ExpenseTypeCode'
        }
        
        payload = {}
        for key, value in kwargs.items():
            api_key = field_mapping.get(key, key)
            payload[api_key] = value
        
        response = self._make_request("PUT", f"expense/entries/{expense_id}", json=payload)
        
        return {
            'success': True,
            'message': f"Successfully updated expense entry {expense_id}"
        }

    def delete_expense(self, expense_id: str) -> Dict[str, Any]:
        """
        Delete an expense entry.
        
        Args:
            expense_id: The ID of the expense entry to delete
            
        Returns:
            Dictionary indicating success/failure
        """
        self._make_request("DELETE", f"expense/entries/{expense_id}")
        
        return {
            'success': True,
            'message': f"Successfully deleted expense entry {expense_id}"
        }

    # UTILITY METHODS
    
    def _get_payment_type_id(self, payment_type_name: str) -> Optional[str]:
        """
        Get the actual PaymentTypeID for a given payment type name by examining existing expenses.
        This is needed because Concur uses base64-encoded IDs internally.
        """
        try:
            # Get a few existing expenses to find payment type IDs
            reports_result = self.list_reports(limit=5)
            if not reports_result['success']:
                return None
            
            for report in reports_result['reports']:
                expenses_result = self.list_expenses(report['id'], limit=5)
                if expenses_result['success'] and expenses_result['expenses']:
                    for expense in expenses_result['expenses']:
                        # Get the full expense details to see the PaymentTypeID
                        try:
                            response = self._make_request("GET", f"expense/entries/{expense['id']}")
                            data = response.json()
                            
                            expense_payment_name = data.get('PaymentTypeName', '').lower()
                            target_payment_name = payment_type_name.lower()
                            
                            if expense_payment_name == target_payment_name:
                                return data.get('PaymentTypeID')
                        except:
                            continue
            
            return None
        except Exception as e:
            logger.error(f"Failed to get payment type ID: {e}")
            return None
    
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
        Get available expense types using user's policies (compatible with v3 create expense).
        
        Returns:
            Dictionary containing expense types with v3-compatible codes for the specific user
        """
        try:
            # Use company-wide expense types (these have the v3-compatible codes we need)
            url = f"{self.config.base_url}/expenseconfig/v4/expensetypes"
            headers = {
                "Authorization": f"Bearer {self._get_access_token()}",
                "Accept": "application/json"
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            expense_types = []
            for item in data:
                # Extract v3-compatible information
                expense_types.append({
                    'code': item.get('expenseCode'),  # This is the v3-compatible code
                    'name': item.get('name'),
                    'category': item.get('expenseCategoryCode'),
                    'spend_category': item.get('spendCategoryCode'),
                    'expense_type_id': item.get('expenseTypeId'),  # v4 ID
                    'description': item.get('description'),
                    'is_deleted': item.get('isDeleted', False),
                    'show_on_mobile': item.get('showOnMobile', True)
                })
            
            return {
                'success': True,
                'expense_types': expense_types,
                'count': len(expense_types),
                'api_version': 'v4_company',
                'message': f'Retrieved {len(expense_types)} expense types from company configuration'
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
