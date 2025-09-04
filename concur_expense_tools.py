#!/usr/bin/env python3
"""
Additional Concur MCP Tools for Expense Management
Provides tools for managing individual expense entries within reports.
"""

from typing import Dict, Any, Optional
from enum import Enum
from concur_expense_sdk import ConcurExpenseSDK, AuthenticationError, NotFoundError, ValidationError, ConcurAPIError


class ConcurAPITopic(Enum):
    """Available topics for Concur API guides and examples."""
    
    # Getting Started
    QUICK_START = "quick_start"
    AUTHENTICATION = "authentication"
    SETUP = "setup"
    
    # Core Operations
    REPORTS = "reports"
    EXPENSES = "expenses"
    
    # Reference Data
    EXPENSE_TYPES = "expense_types"
    PAYMENT_TYPES = "payment_types"
    
    # Common Patterns
    ERROR_HANDLING = "error_handling"
    PAGINATION = "pagination"
    BATCH_OPERATIONS = "batch_operations"
    
    # Troubleshooting
    DEBUGGING = "debugging"
    BEST_PRACTICES = "best_practices"

def _generate_authentication_guide() -> Dict[str, Any]:
    """Generate authentication and setup guide with direct API examples."""
    return {
        "title": "Concur API Authentication Setup",
        "overview": "Learn how to authenticate with Concur APIs using OAuth2 password grant flow.",
        "how_to": {
            "steps": [
                {
                    "step": 1,
                    "title": "Set up credentials",
                    "description": "Gather your Concur API credentials from your administrator",
                    "code": "# Required credentials\nclient_id = 'your_client_id'\nclient_secret = 'your_client_secret'\nusername = 'your_concur_username'\npassword = 'your_concur_password'\n\n# API endpoints\nbase_url = 'https://integration.api.concursolutions.com'\ntoken_url = f'{base_url}/oauth2/v0/token'"
                },
                {
                    "step": 2,
                    "title": "Get access token",
                    "description": "Make OAuth2 token request to get bearer token",
                    "code": "import requests\n\n# Token request payload\ntoken_data = {\n    'client_id': client_id,\n    'client_secret': client_secret,\n    'grant_type': 'password',\n    'username': username,\n    'password': password\n}\n\nheaders = {'Content-Type': 'application/x-www-form-urlencoded'}\n\nresponse = requests.post(token_url, data=token_data, headers=headers)\nresponse.raise_for_status()\n\ntoken_data = response.json()\naccess_token = token_data['access_token']\nexpires_in = token_data.get('expires_in', 3600)\n\nprint(f'Token obtained, expires in {expires_in} seconds')"
                },
                {
                    "step": 3,
                    "title": "Test connection",
                    "description": "Verify token works by making a test API call",
                    "code": "# Test API call - list reports\napi_headers = {\n    'Authorization': f'Bearer {access_token}',\n    'Accept': 'application/json'\n}\n\ntest_response = requests.get(\n    f'{base_url}/api/v3.0/expense/reports?limit=1',\n    headers=api_headers\n)\n\nif test_response.status_code == 200:\n    print('Authentication successful!')\n    print(f'Found {test_response.json().get(\"TotalCount\", 0)} reports')\nelse:\n    print(f'Authentication failed: {test_response.status_code}')"
                }
            ]
        },
        "examples": [
            {
                "title": "Complete Authentication Flow",
                "description": "Full authentication setup with error handling",
                "code": "import requests\nfrom datetime import datetime, timedelta\n\nclass ConcurAuth:\n    def __init__(self, client_id, client_secret, username, password):\n        self.client_id = client_id\n        self.client_secret = client_secret\n        self.username = username\n        self.password = password\n        self.base_url = 'https://integration.api.concursolutions.com'\n        self.token_url = f'{self.base_url}/oauth2/v0/token'\n        self._access_token = None\n        self._token_expiry = None\n    \n    def get_access_token(self):\n        # Return cached token if still valid\n        if self._access_token and self._token_expiry and datetime.now() < self._token_expiry:\n            return self._access_token\n        \n        # Request new token\n        payload = {\n            'client_id': self.client_id,\n            'client_secret': self.client_secret,\n            'grant_type': 'password',\n            'username': self.username,\n            'password': self.password\n        }\n        \n        headers = {'Content-Type': 'application/x-www-form-urlencoded'}\n        \n        try:\n            response = requests.post(self.token_url, data=payload, headers=headers)\n            response.raise_for_status()\n            \n            data = response.json()\n            self._access_token = data['access_token']\n            expires_in = data.get('expires_in', 3600)\n            self._token_expiry = datetime.now() + timedelta(seconds=expires_in)\n            \n            return self._access_token\n            \n        except requests.RequestException as e:\n            raise Exception(f'Authentication failed: {e}')\n    \n    def get_headers(self):\n        return {\n            'Authorization': f'Bearer {self.get_access_token()}',\n            'Accept': 'application/json',\n            'Content-Type': 'application/json'\n        }\n\n# Usage\nauth = ConcurAuth('client_id', 'client_secret', 'username', 'password')\nheaders = auth.get_headers()\n\n# Now use headers for API calls\nresponse = requests.get(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/reports',\n    headers=headers\n)"
            }
        ],
        "dependencies": {
            "credentials": {
                "description": "Concur API credentials from your administrator",
                "required_fields": ["client_id", "client_secret", "username", "password"],
                "note": "These are different from your regular Concur login credentials"
            }
        },
        "api_endpoints": {
            "token_url": "https://integration.api.concursolutions.com/oauth2/v0/token",
            "base_url": "https://integration.api.concursolutions.com"
        }
    }


def _generate_expenses_guide() -> Dict[str, Any]:
    """Generate basic expense operations guide with direct API examples."""
    return {
        "title": "Creating and Managing Expenses via Direct API Calls",
        "overview": "Learn how to create, update, and manage expense entries using direct HTTP requests to Concur's expense APIs.",
        "how_to": {
            "steps": [
                {
                    "step": 1,
                    "title": "Get a report to add expenses to",
                    "description": "List existing reports and select one to add expenses to",
                    "code": "# List reports\nresponse = requests.get(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/reports',\n    headers=headers,\n    params={'limit': 10}\n)\n\nreports = response.json()\nif reports['Items']:\n    report_id = reports['Items'][0]['ID']\n    print(f'Using report: {reports[\"Items\"][0][\"Name\"]} (ID: {report_id})')\nelse:\n    print('No reports found - create one first')"
                },
                {
                    "step": 2,
                    "title": "Get valid expense types",
                    "description": "Retrieve available expense type codes using v4 company API (compatible with v3 create)",
                    "code": "# Get expense types from v4 company API (works with v3 create expense)\nresponse = requests.get(\n    'https://integration.api.concursolutions.com/expenseconfig/v4/expensetypes',\n    headers=headers\n)\n\nexpense_types = response.json()\nprint(f'Available expense types: {len(expense_types)}')\nfor expense_type in expense_types[:5]:  # Show first 5\n    code = expense_type.get('expenseCode')\n    name = expense_type.get('name')\n    print(f\"  {code}: {name}\")\n\n# Extract codes for v3 create expense API\navailable_codes = [et.get('expenseCode') for et in expense_types if et.get('expenseCode')]\nprint(f'\\nCodes for v3 create expense: {list(set(available_codes))}')"
                },
                {
                    "step": 3,
                    "title": "Create expense entry",
                    "description": "Add a new expense to the report",
                    "code": "from datetime import date\n\n# Create expense with required PaymentTypeID\n# Use INCTS (Daily Allowance/Incidentals) - confirmed working expense type\nexpense_data = {\n    'ReportID': report_id,\n    'ExpenseTypeCode': 'INCTS',  # Confirmed working: Daily Allowance/Incidentals\n    'TransactionAmount': 25.50,\n    'TransactionCurrencyCode': 'USD',\n    'TransactionDate': date.today().strftime('%Y-%m-%d'),\n    'BusinessPurpose': 'Daily allowance for business travel',\n    'PaymentTypeID': 'fr1rdFhUGA6l-5FnPPmuq5_HjOMU='  # Known working Cash PaymentTypeID\n}\n\nresponse = requests.post(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/entries',\n    headers=headers,\n    json=expense_data\n)\n\nif response.status_code == 200:\n    expense = response.json()\n    print(f'Created expense: {expense[\"ID\"]}')\nelse:\n    print(f'Error: {response.status_code} - {response.text}')"
                }
            ]
        },
        "examples": [
            {
                "title": "Simple Meal Expense",
                "description": "Create a basic meal expense with minimal required fields",
                "dependencies": {
                    "report_id": "Get from reports list API",
                    "expense_type": "Use 'MEALS' for restaurant expenses"
                },
                "code": "import requests\nfrom datetime import date\n\n# Expense payload\nexpense_payload = {\n    'ReportID': 'rpt_12345',  # From reports list\n    'ExpenseTypeCode': 'MEALS',\n    'TransactionAmount': 25.50,\n    'TransactionCurrencyCode': 'USD',\n    'TransactionDate': date.today().strftime('%Y-%m-%d'),\n    'BusinessPurpose': 'Client lunch meeting'\n}\n\nresponse = requests.post(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/entries',\n    headers=headers,  # From authentication step\n    json=expense_payload\n)\n\nif response.status_code == 200:\n    expense = response.json()\n    print(f'Success! Expense ID: {expense[\"ID\"]}')\n    print(f'URI: {expense[\"URI\"]}')\nelse:\n    print(f'Error {response.status_code}: {response.text}')"
            },
            {
                "title": "Hotel Expense with Full Details",
                "description": "Create hotel expense with location and vendor information",
                "dependencies": {
                    "expense_type": "Use 'LODNG' for hotel/lodging expenses",
                    "country_codes": "Use ISO country codes like 'US', 'CA', 'GB'"
                },
                "code": "# Hotel expense with complete details\nhotel_expense = {\n    'ReportID': 'rpt_12345',\n    'ExpenseTypeCode': 'LODNG',  # Lodging/Hotel\n    'TransactionAmount': 189.99,\n    'TransactionCurrencyCode': 'USD',\n    'TransactionDate': '2024-01-15',\n    'BusinessPurpose': 'Business trip accommodation',\n    'VendorDescription': 'Marriott Downtown Hotel',\n    'LocationName': 'San Francisco',\n    'CountryCode': 'US'\n}\n\nresponse = requests.post(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/entries',\n    headers=headers,\n    json=hotel_expense\n)\n\nprint(f'Hotel expense created: {response.json()[\"ID\"] if response.status_code == 200 else response.text}')"
            },
            {
                "title": "Transportation Expense with Payment Type",
                "description": "Create taxi expense with specific payment method",
                "dependencies": {
                    "payment_types": "Get payment type IDs from v4 API first",
                    "expense_type": "Use 'TAXIC' for taxi/rideshare expenses"
                },
                "code": "# First get payment types (requires user ID from JWT token)\nuser_id = 'your_user_id'  # Extract from JWT token payload\n\n# Get available payment types\npayment_response = requests.get(\n    f'https://integration.api.concursolutions.com/expenseconfig/v4/users/{user_id}/paymenttypes',\n    headers=headers\n)\n\npayment_types = payment_response.json()\ncash_payment_id = None\nfor ptype in payment_types:\n    if ptype['paymentTypeName'].lower() == 'cash':\n        cash_payment_id = ptype['paymentTypeId']\n        break\n\n# Create taxi expense with payment type\ntaxi_expense = {\n    'ReportID': 'rpt_12345',\n    'ExpenseTypeCode': 'TAXIC',\n    'TransactionAmount': 15.75,\n    'TransactionCurrencyCode': 'USD',\n    'TransactionDate': '2024-01-15',\n    'BusinessPurpose': 'Airport transfer',\n    'VendorDescription': 'Uber',\n    'LocationName': 'San Francisco',\n    'PaymentTypeID': cash_payment_id  # Use the ID from payment types\n}\n\nresponse = requests.post(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/entries',\n    headers=headers,\n    json=taxi_expense\n)"
            },
            {
                "title": "List Expenses in Report",
                "description": "Retrieve all expenses for a specific report",
                "code": "# List expenses for a report\nparams = {\n    'reportID': 'rpt_12345',\n    'limit': 25\n}\n\nresponse = requests.get(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/entries',\n    headers=headers,\n    params=params\n)\n\nif response.status_code == 200:\n    expenses = response.json()\n    print(f'Found {len(expenses[\"Items\"])} expenses:')\n    \n    for expense in expenses['Items']:\n        print(f'  {expense[\"ExpenseTypeName\"]}: ${expense[\"TransactionAmount\"]} - {expense[\"BusinessPurpose\"]}')\nelse:\n    print(f'Error: {response.text}')"
            },
            {
                "title": "Update Existing Expense",
                "description": "Modify fields in an existing expense entry",
                "code": "# Update expense entry\nexpense_id = 'exp_67890'\n\n# Only include fields you want to update\nupdate_data = {\n    'TransactionAmount': 30.00,  # New amount\n    'BusinessPurpose': 'Updated: Team dinner with clients',\n    'VendorDescription': 'Updated Restaurant Name'\n}\n\nresponse = requests.put(\n    f'https://integration.api.concursolutions.com/api/v3.0/expense/entries/{expense_id}',\n    headers=headers,\n    json=update_data\n)\n\nif response.status_code == 200:\n    print('Expense updated successfully')\nelse:\n    print(f'Update failed: {response.status_code} - {response.text}')"
            },
            {
                "title": "Delete Expense Entry",
                "description": "Remove an expense from a report",
                "code": "# Delete expense\nexpense_id = 'exp_67890'\n\nresponse = requests.delete(\n    f'https://integration.api.concursolutions.com/api/v3.0/expense/entries/{expense_id}',\n    headers=headers\n)\n\nif response.status_code == 200:\n    print('Expense deleted successfully')\nelse:\n    print(f'Delete failed: {response.status_code} - {response.text}')"
            },
            {
                "title": "Bulk Expense Creation",
                "description": "Create multiple expenses efficiently with error handling",
                "code": "# Bulk expense creation with error handling\nexpenses_to_create = [\n    {\n        'ReportID': 'rpt_12345',\n        'ExpenseTypeCode': 'MEALS',\n        'TransactionAmount': 25.50,\n        'TransactionDate': '2024-01-15',\n        'BusinessPurpose': 'Breakfast meeting'\n    },\n    {\n        'ReportID': 'rpt_12345',\n        'ExpenseTypeCode': 'TAXIC',\n        'TransactionAmount': 18.75,\n        'TransactionDate': '2024-01-15',\n        'BusinessPurpose': 'Airport transfer'\n    },\n    {\n        'ReportID': 'rpt_12345',\n        'ExpenseTypeCode': 'LODNG',\n        'TransactionAmount': 195.00,\n        'TransactionDate': '2024-01-15',\n        'BusinessPurpose': 'Hotel accommodation'\n    }\n]\n\ncreated_expenses = []\nfailed_expenses = []\n\nfor expense_data in expenses_to_create:\n    try:\n        response = requests.post(\n            'https://integration.api.concursolutions.com/api/v3.0/expense/entries',\n            headers=headers,\n            json=expense_data\n        )\n        \n        if response.status_code == 200:\n            expense = response.json()\n            created_expenses.append({\n                'id': expense['ID'],\n                'amount': expense_data['TransactionAmount'],\n                'type': expense_data['ExpenseTypeCode']\n            })\n            print(f'✅ Created {expense_data[\"ExpenseTypeCode\"]} expense: ${expense_data[\"TransactionAmount\"]}')\n        else:\n            failed_expenses.append({\n                'data': expense_data,\n                'error': response.text\n            })\n            print(f'❌ Failed to create {expense_data[\"ExpenseTypeCode\"]} expense: {response.status_code}')\n            \n    except Exception as e:\n        failed_expenses.append({\n            'data': expense_data,\n            'error': str(e)\n        })\n        print(f'❌ Exception creating expense: {e}')\n\nprint(f'\\nSummary: {len(created_expenses)} created, {len(failed_expenses)} failed')"
            },
            {
                "title": "Advanced Expense with Custom Fields",
                "description": "Create expense with all available fields and custom data",
                "code": "# Advanced expense creation with all fields\nfrom datetime import date, datetime\nimport json\n\n# First get user's expense types and payment types\nuser_id = 'your_user_id'  # Extract from JWT token\n\n# Get expense types\nexp_types_response = requests.get(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/expensetypes',\n    headers=headers\n)\nexpense_types = {item['Code']: item['Name'] for item in exp_types_response.json()['Items']}\n\n# Get payment types\npayment_response = requests.get(\n    f'https://integration.api.concursolutions.com/expenseconfig/v4/users/{user_id}/paymenttypes',\n    headers=headers\n)\npayment_types = {item['paymentTypeName']: item['paymentTypeId'] for item in payment_response.json()}\n\n# Create comprehensive expense\nadvanced_expense = {\n    'ReportID': 'rpt_12345',\n    'ExpenseTypeCode': 'MEALS',\n    'TransactionAmount': 87.50,\n    'TransactionCurrencyCode': 'USD',\n    'TransactionDate': date.today().strftime('%Y-%m-%d'),\n    'BusinessPurpose': 'Client dinner meeting - Q1 planning session',\n    'VendorDescription': 'The Capital Grille Downtown',\n    'LocationName': 'San Francisco, CA',\n    'CountryCode': 'US',\n    'PaymentTypeID': payment_types.get('Company Card', payment_types.get('Cash')),\n    'Comment': 'Dinner with 3 clients to discuss upcoming project milestones',\n    'HasReceipt': True,\n    'ReceiptRequired': True\n}\n\n# Add optional fields if available\nif 'MEALS' in expense_types:\n    print(f'Using expense type: {expense_types[\"MEALS\"]}')\n\nresponse = requests.post(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/entries',\n    headers=headers,\n    json=advanced_expense\n)\n\nif response.status_code == 200:\n    expense = response.json()\n    print('✅ Advanced expense created successfully:')\n    print(f'   ID: {expense[\"ID\"]}')\n    print(f'   Amount: ${advanced_expense[\"TransactionAmount\"]}')\n    print(f'   Vendor: {advanced_expense[\"VendorDescription\"]}')\n    print(f'   Purpose: {advanced_expense[\"BusinessPurpose\"]}')\nelse:\n    print(f'❌ Failed to create advanced expense:')\n    print(f'   Status: {response.status_code}')\n    print(f'   Error: {response.text}')"
            },
            {
                "title": "Expense Validation and Error Handling",
                "description": "Comprehensive validation and error handling patterns",
                "code": "# Expense validation and error handling\nimport re\nfrom datetime import datetime, date\n\ndef validate_expense_data(expense_data):\n    \"\"\"Validate expense data before submission.\"\"\"\n    errors = []\n    \n    # Required fields\n    required_fields = ['ReportID', 'ExpenseTypeCode', 'TransactionAmount', 'TransactionDate']\n    for field in required_fields:\n        if not expense_data.get(field):\n            errors.append(f'Missing required field: {field}')\n    \n    # Amount validation\n    amount = expense_data.get('TransactionAmount', 0)\n    if not isinstance(amount, (int, float)) or amount <= 0:\n        errors.append('TransactionAmount must be a positive number')\n    \n    # Date validation\n    try:\n        date_str = expense_data.get('TransactionDate', '')\n        expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()\n        if expense_date > date.today():\n            errors.append('TransactionDate cannot be in the future')\n    except ValueError:\n        errors.append('TransactionDate must be in YYYY-MM-DD format')\n    \n    # Currency code validation\n    currency = expense_data.get('TransactionCurrencyCode', 'USD')\n    if not re.match(r'^[A-Z]{3}$', currency):\n        errors.append('TransactionCurrencyCode must be a 3-letter currency code')\n    \n    return errors\n\ndef create_expense_with_validation(expense_data):\n    \"\"\"Create expense with comprehensive validation and error handling.\"\"\"\n    \n    # Validate data\n    validation_errors = validate_expense_data(expense_data)\n    if validation_errors:\n        return {\n            'success': False,\n            'error': 'Validation failed',\n            'details': validation_errors\n        }\n    \n    # Attempt to create expense\n    try:\n        response = requests.post(\n            'https://integration.api.concursolutions.com/api/v3.0/expense/entries',\n            headers=headers,\n            json=expense_data,\n            timeout=30  # Add timeout\n        )\n        \n        if response.status_code == 200:\n            return {\n                'success': True,\n                'expense': response.json(),\n                'message': 'Expense created successfully'\n            }\n        elif response.status_code == 400:\n            return {\n                'success': False,\n                'error': 'Bad Request',\n                'details': response.json() if response.content else 'Invalid request data'\n            }\n        elif response.status_code == 401:\n            return {\n                'success': False,\n                'error': 'Authentication failed',\n                'details': 'Token may be expired or invalid'\n            }\n        elif response.status_code == 404:\n            return {\n                'success': False,\n                'error': 'Not Found',\n                'details': 'Report ID may not exist or be accessible'\n            }\n        else:\n            return {\n                'success': False,\n                'error': f'HTTP {response.status_code}',\n                'details': response.text\n            }\n            \n    except requests.exceptions.Timeout:\n        return {\n            'success': False,\n            'error': 'Request timeout',\n            'details': 'The request took too long to complete'\n        }\n    except requests.exceptions.ConnectionError:\n        return {\n            'success': False,\n            'error': 'Connection error',\n            'details': 'Unable to connect to Concur API'\n        }\n    except Exception as e:\n        return {\n            'success': False,\n            'error': 'Unexpected error',\n            'details': str(e)\n        }\n\n# Example usage\ntest_expense = {\n    'ReportID': 'rpt_12345',\n    'ExpenseTypeCode': 'MEALS',\n    'TransactionAmount': 45.75,\n    'TransactionCurrencyCode': 'USD',\n    'TransactionDate': '2024-01-15',\n    'BusinessPurpose': 'Team lunch meeting'\n}\n\nresult = create_expense_with_validation(test_expense)\nif result['success']:\n    print(f'✅ {result[\"message\"]}')\n    print(f'   Expense ID: {result[\"expense\"][\"ID\"]}')\nelse:\n    print(f'❌ {result[\"error\"]}: {result[\"details\"]}')"
            }
        ],
        "dependencies": {
            "expense_types": {
                "description": "Valid expense type codes must be retrieved from v4 company API",
                "how_to_get": "GET /expenseconfig/v4/expensetypes",
                "available_codes": ["COCARMILE", "INCTS", "JPYPTRAN", "LODGING", "MEALS", "MFUEL", "OTHER", "OTHERNP", "PCARMILE"],
                "example": "Use 'OTHER' for general expenses, 'LODGING' for hotels, 'MEALS' for restaurants",
                "note": "v3 expense types API returns 403 Forbidden, use v4 company API instead"
            },
            "payment_types": {
                "description": "PaymentTypeID is REQUIRED for v3 create expense API",
                "working_id": "fr1rdFhUGA6l-5FnPPmuq5_HjOMU=",
                "payment_type": "Cash",
                "note": "v4 payment types API IDs don't work with v3 create, use the known working Cash ID",
                "how_to_get_others": "Extract PaymentTypeID from existing expenses via GET /api/v3.0/expense/entries/{expenseId}"
            },
            "report_id": {
                "description": "Expenses must be added to existing draft reports",
                "how_to_get": "GET /api/v3.0/expense/reports",
                "example": "Get first report: reports['Items'][0]['ID']",
                "note": "Cannot add expenses to submitted reports"
            }
        },
        "api_endpoints": {
            "expense_entries": "/api/v3.0/expense/entries",
            "expense_types_working": "/expenseconfig/v4/expensetypes",
            "expense_types_v3_broken": "/api/v3.0/expense/expensetypes",
            "payment_types_v4": "/expenseconfig/v4/users/{userId}/paymenttypes",
            "reports": "/api/v3.0/expense/reports"
        }
    }


def _generate_expense_types_guide() -> Dict[str, Any]:
    """Generate expense types guide with working v4 API approach."""
    return {
        "title": "Getting Expense Types - Working Solution",
        "overview": "Learn how to retrieve expense types using the v4 company API that works with v3 create expense.",
        "how_to": {
            "steps": [
                {
                    "step": 1,
                    "title": "Get expense types from v4 company API",
                    "description": "Use the v4 company endpoint that provides v3-compatible codes",
                    "code": "# Get expense types from v4 company API\nresponse = requests.get(\n    'https://integration.api.concursolutions.com/expenseconfig/v4/expensetypes',\n    headers=headers\n)\n\nif response.status_code == 200:\n    expense_types = response.json()\n    print(f'Found {len(expense_types)} expense types')\n    \n    # Extract v3-compatible codes\n    available_codes = []\n    for et in expense_types:\n        code = et.get('expenseCode')\n        name = et.get('name')\n        if code:\n            available_codes.append(code)\n            print(f'  {code}: {name}')\n    \n    print(f'\\nAvailable codes for v3 create expense: {sorted(set(available_codes))}')\nelse:\n    print(f'Error: {response.status_code} - {response.text}')"
                },
                {
                    "step": 2,
                    "title": "Test expense creation with available codes",
                    "description": "Create expenses using the codes from step 1",
                    "code": "# Test creating expense with confirmed working codes\nworking_codes = ['INCTS', 'OTHER']  # Confirmed working codes\n\nfor code in working_codes:\n    expense_data = {\n        'ReportID': report_id,  # From reports list\n        'ExpenseTypeCode': code,\n        'TransactionAmount': 25.00,\n        'TransactionCurrencyCode': 'USD',\n        'TransactionDate': '2024-01-15',\n        'BusinessPurpose': f'Business expense - {\"Daily allowance\" if code == \"INCTS\" else \"General travel\"}',\n        'PaymentTypeID': 'fr1rdFhUGA6l-5FnPPmuq5_HjOMU='  # Known working Cash ID\n    }\n    \n    response = requests.post(\n        'https://integration.api.concursolutions.com/api/v3.0/expense/entries',\n        headers=headers,\n        json=expense_data\n    )\n    \n    if response.status_code == 200:\n        expense = response.json()\n        print(f'✅ {code} expense created: {expense[\"ID\"]}')\n    else:\n        print(f'❌ {code} failed: {response.status_code}')\n\n# Recommended: Use INCTS as default\nprint('💡 Recommendation: Use INCTS as default expense type for reliable creation')"
                }
            ]
        },
        "key_findings": {
            "working_solution": {
                "expense_types_api": "/expenseconfig/v4/expensetypes",
                "create_expense_api": "/api/v3.0/expense/entries",
                "required_payment_id": "fr1rdFhUGA6l-5FnPPmuq5_HjOMU=",
                "payment_type": "Cash"
            },
            "why_this_works": [
                "v4 company API provides expense types with v3-compatible 'expenseCode' field",
                "v3 create expense API requires PaymentTypeID (not optional)",
                "Known working PaymentTypeID bridges v4 expense types with v3 create expense",
                "Company-wide expense types include all codes available to users"
            ],
            "what_doesnt_work": [
                "v3 expense types API returns 403 Forbidden",
                "v4 user policy expense types don't have 'expenseCode' field",
                "v4 payment types API IDs are incompatible with v3 create expense",
                "Direct user expense types endpoint returns 500 Server Error"
            ]
        },
        "available_codes": {
            "description": "Expense type codes available from v4 company API",
            "working_codes": [
                {"code": "INCTS", "description": "Daily Allowance (Incidentals)", "status": "✅ WORKING"},
                {"code": "OTHER", "description": "General Travel Expenses", "status": "✅ WORKING"}
            ],
            "non_working_codes": [
                {"code": "COCARMILE", "description": "Company car mileage", "status": "❌ Not in user's expense group"},
                {"code": "JPYPTRAN", "description": "Japan transport", "status": "❌ Not in user's expense group"},
                {"code": "LODGING", "description": "Hotel/accommodation", "status": "❌ Not in user's expense group"},
                {"code": "MEALS", "description": "Restaurant/meals", "status": "❌ Not in user's expense group"},
                {"code": "MFUEL", "description": "Motor fuel", "status": "❌ Other error"},
                {"code": "OTHERNP", "description": "Other non-personal", "status": "❌ Not in user's expense group"},
                {"code": "PCARMILE", "description": "Personal car mileage", "status": "❌ Not in user's expense group"}
            ],
            "recommendation": "Use 'INCTS' as default - it's confirmed working for all users tested",
            "note": "Non-working codes require Concur administrator to add them to user's expense group"
        }
    }


def _generate_reports_guide() -> Dict[str, Any]:
    """Generate basic report operations guide with direct API examples."""
    return {
        "title": "Managing Expense Reports via Direct API Calls",
        "overview": "Learn how to create, list, update, and manage expense reports using direct HTTP requests.",
        "how_to": {
            "steps": [
                {
                    "step": 1,
                    "title": "List existing reports",
                    "description": "Get a list of current expense reports",
                    "code": "# List reports with pagination\nparams = {\n    'limit': 10,  # Max 100\n    'offset': 0   # For pagination\n}\n\nresponse = requests.get(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/reports',\n    headers=headers,\n    params=params\n)\n\nreports = response.json()\nprint(f'Found {reports[\"TotalCount\"]} total reports')\nfor report in reports['Items']:\n    print(f'  {report[\"Name\"]}: ${report[\"Total\"]} ({report[\"ApprovalStatusName\"]})')"
                },
                {
                    "step": 2,
                    "title": "Create new report",
                    "description": "Create a new expense report to hold expenses",
                    "code": "# Create new report\nreport_data = {\n    'Name': 'Business Trip - January 2024',\n    'Purpose': 'Client meetings and conference attendance',\n    'BusinessPurpose': 'Sales meetings with key clients in San Francisco',\n    'CurrencyCode': 'USD',\n    'Country': 'US'\n}\n\nresponse = requests.post(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/reports',\n    headers=headers,\n    json=report_data\n)\n\nif response.status_code == 200:\n    report = response.json()\n    print(f'Created report: {report[\"ID\"]}')\n    print(f'URI: {report[\"URI\"]}')\nelse:\n    print(f'Error: {response.status_code} - {response.text}')"
                }
            ]
        },
        "examples": [
            {
                "title": "Create Business Trip Report",
                "description": "Create a new expense report for a business trip",
                "code": "import requests\n\n# Report creation payload\nreport_payload = {\n    'Name': 'Q1 Sales Conference - March 2024',\n    'Purpose': 'Annual sales conference attendance',\n    'BusinessPurpose': 'Attend quarterly sales meeting and client presentations',\n    'CurrencyCode': 'USD',\n    'Country': 'US'\n}\n\nresponse = requests.post(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/reports',\n    headers=headers,  # From authentication\n    json=report_payload\n)\n\nif response.status_code == 200:\n    new_report = response.json()\n    report_id = new_report['ID']\n    print(f'Success! Created report: {report_id}')\n    print(f'Report URI: {new_report[\"URI\"]}')\nelse:\n    print(f'Failed to create report: {response.status_code}')\n    print(response.text)"
            },
            {
                "title": "List Reports with Filtering",
                "description": "Get reports with specific criteria and pagination",
                "code": "# List reports with filtering\nparams = {\n    'limit': 25,\n    'offset': 0,\n    'user': 'specific_user_id'  # Optional: filter by user\n}\n\nresponse = requests.get(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/reports',\n    headers=headers,\n    params=params\n)\n\nif response.status_code == 200:\n    data = response.json()\n    print(f'Total reports: {data[\"TotalCount\"]}')\n    print(f'Showing {len(data[\"Items\"])} reports:')\n    \n    for report in data['Items']:\n        print(f'  ID: {report[\"ID\"]}')\n        print(f'  Name: {report[\"Name\"]}')\n        print(f'  Total: ${report[\"Total\"]} {report[\"CurrencyCode\"]}')\n        print(f'  Status: {report[\"ApprovalStatusName\"]}')\n        print(f'  Created: {report[\"CreateDate\"]}')\n        print('  ---')\nelse:\n    print(f'Error listing reports: {response.text}')"
            },
            {
                "title": "Get Specific Report Details",
                "description": "Retrieve detailed information for a single report",
                "code": "# Get specific report\nreport_id = 'rpt_12345'\n\nresponse = requests.get(\n    f'https://integration.api.concursolutions.com/api/v3.0/expense/reports/{report_id}',\n    headers=headers\n)\n\nif response.status_code == 200:\n    report = response.json()\n    print(f'Report Details:')\n    print(f'  Name: {report[\"Name\"]}')\n    print(f'  Purpose: {report[\"Purpose\"]}')\n    print(f'  Business Purpose: {report[\"BusinessPurpose\"]}')\n    print(f'  Total: ${report[\"Total\"]} {report[\"CurrencyCode\"]}')\n    print(f'  Status: {report[\"ApprovalStatusName\"]}')\n    print(f'  Workflow Step: {report[\"WorkflowStepName\"]}')\n    print(f'  Owner: {report[\"OwnerName\"]}')\n    print(f'  Country: {report[\"Country\"]}')\n    print(f'  Created: {report[\"CreateDate\"]}')\n    print(f'  Last Modified: {report[\"LastModifiedDate\"]}')\nelse:\n    print(f'Report not found: {response.text}')"
            },
            {
                "title": "Update Report Information",
                "description": "Modify fields in an existing report",
                "code": "# Update report\nreport_id = 'rpt_12345'\n\n# Only include fields to update\nupdate_data = {\n    'Name': 'Updated Report Name - Q1 Conference',\n    'Purpose': 'Updated purpose description',\n    'BusinessPurpose': 'Updated business justification for expenses'\n}\n\nresponse = requests.put(\n    f'https://integration.api.concursolutions.com/api/v3.0/expense/reports/{report_id}',\n    headers=headers,\n    json=update_data\n)\n\nif response.status_code == 200:\n    print('Report updated successfully')\nelse:\n    print(f'Update failed: {response.status_code} - {response.text}')"
            },
            {
                "title": "Delete Report",
                "description": "Delete an expense report (only if it has no expenses)",
                "code": "# Delete report (must be empty)\nreport_id = 'rpt_12345'\n\nresponse = requests.delete(\n    f'https://integration.api.concursolutions.com/api/v3.0/expense/reports/{report_id}',\n    headers=headers\n)\n\nif response.status_code == 200:\n    print('Report deleted successfully')\nelse:\n    print(f'Delete failed: {response.status_code} - {response.text}')\n    print('Note: Reports with expenses cannot be deleted')"
            },
            {
                "title": "Bulk Report Operations",
                "description": "Perform operations on multiple reports efficiently",
                "code": "# Bulk report operations\nimport concurrent.futures\nfrom datetime import datetime, timedelta\n\ndef get_report_summary(report_id):\n    \"\"\"Get summary info for a single report.\"\"\"\n    try:\n        response = requests.get(\n            f'https://integration.api.concursolutions.com/api/v3.0/expense/reports/{report_id}',\n            headers=headers,\n            timeout=10\n        )\n        \n        if response.status_code == 200:\n            data = response.json()\n            return {\n                'id': report_id,\n                'name': data.get('Name'),\n                'total': data.get('Total', 0),\n                'currency': data.get('CurrencyCode'),\n                'status': data.get('ApprovalStatusName'),\n                'created': data.get('CreateDate'),\n                'success': True\n            }\n        else:\n            return {\n                'id': report_id,\n                'error': f'HTTP {response.status_code}',\n                'success': False\n            }\n    except Exception as e:\n        return {\n            'id': report_id,\n            'error': str(e),\n            'success': False\n        }\n\n# Get list of report IDs\nresponse = requests.get(\n    'https://integration.api.concursolutions.com/api/v3.0/expense/reports',\n    headers=headers,\n    params={'limit': 50}\n)\n\nif response.status_code == 200:\n    reports_data = response.json()\n    report_ids = [item['ID'] for item in reports_data['Items']]\n    \n    print(f'Processing {len(report_ids)} reports...')\n    \n    # Process reports in parallel\n    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:\n        future_to_report = {executor.submit(get_report_summary, report_id): report_id \n                           for report_id in report_ids}\n        \n        successful_reports = []\n        failed_reports = []\n        \n        for future in concurrent.futures.as_completed(future_to_report):\n            result = future.result()\n            \n            if result['success']:\n                successful_reports.append(result)\n                print(f'✅ {result[\"name\"]}: ${result[\"total\"]} ({result[\"status\"]})')\n            else:\n                failed_reports.append(result)\n                print(f'❌ Report {result[\"id\"]}: {result[\"error\"]}')\n    \n    # Summary statistics\n    total_amount = sum(r['total'] for r in successful_reports if r['total'])\n    print(f'\\n📊 Summary:')\n    print(f'   Successful: {len(successful_reports)}')\n    print(f'   Failed: {len(failed_reports)}')\n    print(f'   Total Amount: ${total_amount:.2f}')\n    \n    # Group by status\n    status_groups = {}\n    for report in successful_reports:\n        status = report.get('status', 'Unknown')\n        if status not in status_groups:\n            status_groups[status] = []\n        status_groups[status].append(report)\n    \n    print(f'\\n📋 By Status:')\n    for status, reports in status_groups.items():\n        total = sum(r['total'] for r in reports if r['total'])\n        print(f'   {status}: {len(reports)} reports, ${total:.2f}')\n\nelse:\n    print(f'Failed to get reports list: {response.status_code}')"
            },
            {
                "title": "Report Workflow Management",
                "description": "Advanced report status and workflow operations",
                "code": "# Report workflow management\nfrom datetime import datetime, date\n\ndef check_report_readiness(report_id):\n    \"\"\"Check if a report is ready for submission.\"\"\"\n    \n    # Get report details\n    report_response = requests.get(\n        f'https://integration.api.concursolutions.com/api/v3.0/expense/reports/{report_id}',\n        headers=headers\n    )\n    \n    if report_response.status_code != 200:\n        return {'ready': False, 'error': 'Could not retrieve report'}\n    \n    report = report_response.json()\n    \n    # Get report expenses\n    expenses_response = requests.get(\n        'https://integration.api.concursolutions.com/api/v3.0/expense/entries',\n        headers=headers,\n        params={'reportID': report_id, 'limit': 100}\n    )\n    \n    if expenses_response.status_code != 200:\n        return {'ready': False, 'error': 'Could not retrieve expenses'}\n    \n    expenses = expenses_response.json()['Items']\n    \n    # Check readiness criteria\n    issues = []\n    \n    # Must have expenses\n    if not expenses:\n        issues.append('Report has no expenses')\n    \n    # Check for missing receipts\n    missing_receipts = []\n    for expense in expenses:\n        if expense.get('ReceiptRequired') and not expense.get('HasReceipt'):\n            missing_receipts.append({\n                'id': expense.get('ID'),\n                'type': expense.get('ExpenseTypeName'),\n                'amount': expense.get('TransactionAmount')\n            })\n    \n    if missing_receipts:\n        issues.append(f'{len(missing_receipts)} expenses missing required receipts')\n    \n    # Check for empty business purposes\n    empty_purposes = [e for e in expenses if not e.get('BusinessPurpose', '').strip()]\n    if empty_purposes:\n        issues.append(f'{len(empty_purposes)} expenses missing business purpose')\n    \n    # Check report fields\n    if not report.get('Name', '').strip():\n        issues.append('Report name is empty')\n    \n    if not report.get('BusinessPurpose', '').strip():\n        issues.append('Report business purpose is empty')\n    \n    return {\n        'ready': len(issues) == 0,\n        'issues': issues,\n        'report_name': report.get('Name'),\n        'total_expenses': len(expenses),\n        'total_amount': report.get('Total', 0),\n        'missing_receipts': missing_receipts,\n        'status': report.get('ApprovalStatusName')\n    }\n\ndef prepare_report_for_submission(report_id):\n    \"\"\"Prepare a report for submission by fixing common issues.\"\"\"\n    \n    readiness = check_report_readiness(report_id)\n    \n    if readiness['ready']:\n        print(f'✅ Report {report_id} is ready for submission')\n        return {'success': True, 'message': 'Report is ready'}\n    \n    print(f'⚠️  Report {report_id} has issues:')\n    for issue in readiness['issues']:\n        print(f'   - {issue}')\n    \n    # Auto-fix what we can\n    fixes_applied = []\n    \n    # Fix empty report name\n    if 'Report name is empty' in readiness['issues']:\n        today = date.today().strftime('%Y-%m-%d')\n        update_data = {'Name': f'Expense Report - {today}'}\n        \n        response = requests.put(\n            f'https://integration.api.concursolutions.com/api/v3.0/expense/reports/{report_id}',\n            headers=headers,\n            json=update_data\n        )\n        \n        if response.status_code == 200:\n            fixes_applied.append('Added default report name')\n    \n    # Fix empty business purpose\n    if 'Report business purpose is empty' in readiness['issues']:\n        update_data = {'BusinessPurpose': 'Business expenses for company operations'}\n        \n        response = requests.put(\n            f'https://integration.api.concursolutions.com/api/v3.0/expense/reports/{report_id}',\n            headers=headers,\n            json=update_data\n        )\n        \n        if response.status_code == 200:\n            fixes_applied.append('Added default business purpose')\n    \n    if fixes_applied:\n        print(f'🔧 Applied fixes:')\n        for fix in fixes_applied:\n            print(f'   ✅ {fix}')\n    \n    # Re-check readiness\n    updated_readiness = check_report_readiness(report_id)\n    \n    return {\n        'success': updated_readiness['ready'],\n        'fixes_applied': fixes_applied,\n        'remaining_issues': updated_readiness['issues'],\n        'message': 'Ready for submission' if updated_readiness['ready'] else 'Manual fixes still needed'\n    }\n\n# Example usage\ntest_report_id = 'rpt_12345'\nresult = prepare_report_for_submission(test_report_id)\n\nif result['success']:\n    print(f'\\n🎉 Report is ready for submission!')\nelse:\n    print(f'\\n⚠️  Manual fixes needed:')\n    for issue in result.get('remaining_issues', []):\n        print(f'   - {issue}')"
            },
            {
                "title": "Report Analytics and Insights",
                "description": "Analyze reports for insights and patterns",
                "code": "# Report analytics and insights\nfrom collections import defaultdict, Counter\nfrom datetime import datetime, timedelta\nimport statistics\n\ndef analyze_expense_reports(days_back=30):\n    \"\"\"Analyze expense reports for insights and patterns.\"\"\"\n    \n    # Get reports from the last N days\n    cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')\n    \n    # Get all reports (paginated)\n    all_reports = []\n    offset = 0\n    limit = 50\n    \n    while True:\n        params = {'limit': limit, 'offset': offset}\n        response = requests.get(\n            'https://integration.api.concursolutions.com/api/v3.0/expense/reports',\n            headers=headers,\n            params=params\n        )\n        \n        if response.status_code != 200:\n            break\n            \n        data = response.json()\n        reports = data['Items']\n        \n        if not reports:\n            break\n            \n        # Filter by date\n        for report in reports:\n            if report.get('CreateDate', '') >= cutoff_date:\n                all_reports.append(report)\n        \n        offset += limit\n        \n        # Stop if we've got all reports\n        if len(reports) < limit:\n            break\n    \n    print(f'📊 Analyzing {len(all_reports)} reports from last {days_back} days')\n    \n    if not all_reports:\n        print('No reports found in the specified period')\n        return\n    \n    # Basic statistics\n    total_amount = sum(r.get('Total', 0) for r in all_reports)\n    amounts = [r.get('Total', 0) for r in all_reports if r.get('Total')]\n    \n    print(f'\\n💰 Financial Summary:')\n    print(f'   Total Amount: ${total_amount:,.2f}')\n    print(f'   Average Report: ${statistics.mean(amounts):,.2f}')\n    print(f'   Median Report: ${statistics.median(amounts):,.2f}')\n    print(f'   Largest Report: ${max(amounts):,.2f}')\n    print(f'   Smallest Report: ${min(amounts):,.2f}')\n    \n    # Status analysis\n    status_counts = Counter(r.get('ApprovalStatusName', 'Unknown') for r in all_reports)\n    status_amounts = defaultdict(float)\n    \n    for report in all_reports:\n        status = report.get('ApprovalStatusName', 'Unknown')\n        status_amounts[status] += report.get('Total', 0)\n    \n    print(f'\\n📋 Status Breakdown:')\n    for status, count in status_counts.most_common():\n        amount = status_amounts[status]\n        print(f'   {status}: {count} reports, ${amount:,.2f}')\n    \n    # Currency analysis\n    currency_counts = Counter(r.get('CurrencyCode', 'USD') for r in all_reports)\n    print(f'\\n💱 Currency Distribution:')\n    for currency, count in currency_counts.most_common():\n        print(f'   {currency}: {count} reports')\n    \n    # Time-based analysis\n    monthly_totals = defaultdict(float)\n    for report in all_reports:\n        create_date = report.get('CreateDate', '')\n        if create_date:\n            try:\n                month = create_date[:7]  # YYYY-MM\n                monthly_totals[month] += report.get('Total', 0)\n            except:\n                pass\n    \n    print(f'\\n📅 Monthly Trends:')\n    for month in sorted(monthly_totals.keys()):\n        print(f'   {month}: ${monthly_totals[month]:,.2f}')\n    \n    # Get expense details for deeper analysis\n    expense_types = defaultdict(float)\n    expense_counts = defaultdict(int)\n    \n    print(f'\\n🔍 Analyzing expense details...')\n    \n    for i, report in enumerate(all_reports[:10]):  # Limit to first 10 for performance\n        report_id = report['ID']\n        \n        # Get expenses for this report\n        exp_response = requests.get(\n            'https://integration.api.concursolutions.com/api/v3.0/expense/entries',\n            headers=headers,\n            params={'reportID': report_id, 'limit': 100}\n        )\n        \n        if exp_response.status_code == 200:\n            expenses = exp_response.json()['Items']\n            \n            for expense in expenses:\n                exp_type = expense.get('ExpenseTypeName', 'Unknown')\n                amount = expense.get('TransactionAmount', 0)\n                \n                expense_types[exp_type] += amount\n                expense_counts[exp_type] += 1\n        \n        print(f'   Processed report {i+1}/10', end='\\r')\n    \n    print(f'\\n\\n🏷️  Top Expense Types:')\n    for exp_type, total in sorted(expense_types.items(), key=lambda x: x[1], reverse=True)[:10]:\n        count = expense_counts[exp_type]\n        avg = total / count if count > 0 else 0\n        print(f'   {exp_type}: {count} expenses, ${total:,.2f} total, ${avg:.2f} avg')\n    \n    return {\n        'total_reports': len(all_reports),\n        'total_amount': total_amount,\n        'average_amount': statistics.mean(amounts),\n        'status_breakdown': dict(status_counts),\n        'currency_distribution': dict(currency_counts),\n        'expense_types': dict(expense_types)\n    }\n\n# Run analysis\ninsights = analyze_expense_reports(days_back=60)\nprint('\\n✅ Analysis complete!')"
            }
        ],
        "dependencies": {
            "currency_codes": {
                "description": "Use standard ISO currency codes",
                "examples": ["USD", "EUR", "GBP", "CAD", "JPY"],
                "default": "USD"
            },
            "country_codes": {
                "description": "Use ISO country codes",
                "examples": ["US", "CA", "GB", "FR", "DE", "JP"],
                "default": "US"
            }
        },
        "api_endpoints": {
            "reports": "/api/v3.0/expense/reports",
            "specific_report": "/api/v3.0/expense/reports/{reportId}"
        }
    }


def create_expense_tools(mcp, concur_sdk: ConcurExpenseSDK):
    """Add expense-related tools to the MCP server."""
    
    @mcp.tool()
    def get_concur_api_guide(
        topic: ConcurAPITopic,
        include_examples: bool = True,
        include_howto: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive Concur API guide with direct API call examples and how-to instructions.
        
        The examples show raw HTTP requests using Python requests library, not SDK usage.
        The SDK code is used as reference to understand the correct API patterns.
        
        Args:
            topic: The API topic to get guidance for
            include_examples: Whether to include code examples (default: True)
            include_howto: Whether to include step-by-step how-to instructions (default: True)
        
        Returns:
            Comprehensive guide with examples, how-tos, and reference information
        """
        try:
            # Map topics to their content generators
            topic_generators = {
                ConcurAPITopic.AUTHENTICATION: _generate_authentication_guide,
                ConcurAPITopic.SETUP: _generate_authentication_guide,  # Same as auth
                ConcurAPITopic.EXPENSES: _generate_expenses_guide,
                ConcurAPITopic.EXPENSE_TYPES: _generate_expense_types_guide,
                ConcurAPITopic.REPORTS: _generate_reports_guide,
            }
            
            # Get the appropriate generator
            generator = topic_generators.get(topic)
            if not generator:
                return {
                    'success': False,
                    'error': f'Documentation not yet available for topic: {topic.value}',
                    'available_topics': [t.value for t in topic_generators.keys()],
                    'message': f'Topic {topic.value} is not implemented yet. Available topics: {", ".join([t.value for t in topic_generators.keys()])}'
                }
            
            # Generate the content
            guide_content = generator()
            
            # Filter content based on parameters
            if not include_howto:
                guide_content.pop('how_to', None)
            
            if not include_examples:
                guide_content.pop('examples', None)
            
            return {
                'success': True,
                'topic': topic.value,
                **guide_content,
                'message': f'Retrieved guide for {topic.value}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to generate guide for {topic.value}: {str(e)}'
            }
    
    @mcp.tool()
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

    @mcp.tool()
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

    @mcp.tool()
    def create_concur_expense(report_id: str, amount: float, expense_type: str = "INCTS", 
                             currency_code: str = "USD", transaction_date: str = None,
                             business_purpose: str = "", vendor_description: str = "",
                             city_name: str = "", country_code: str = "US",
                             payment_type: str = "CASH") -> Dict[str, Any]:
        """
        Create a new expense entry in a report.
        
        Args:
            report_id: The ID of the report to add the expense to
            amount: Transaction amount
            expense_type: Type of expense (default: 'INCTS' - Daily Allowance/Incidentals). Confirmed working types: 'INCTS', 'OTHER'
            currency_code: Currency code (default: USD)
            transaction_date: Date of transaction in YYYY-MM-DD format (default: today)
            business_purpose: Business purpose of the expense
            vendor_description: Vendor/merchant description
            city_name: City where expense occurred
            country_code: Country code (default: US)
            payment_type: Payment method (default: CASH) - automatically uses known working PaymentTypeID
        
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

    @mcp.tool()
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

    @mcp.tool()
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

    @mcp.tool()
    def get_concur_expense_types() -> Dict[str, Any]:
        """
        Get available expense types from Concur using the working v4 company API.
        
        This function retrieves expense types with v3-compatible codes that can be used
        with the create_concur_expense function. Uses /expenseconfig/v4/expensetypes
        endpoint which provides the 'expenseCode' field needed for v3 expense creation.
        
        Returns:
            Dictionary containing expense types with codes like: OTHER, LODGING, MEALS, 
            COCARMILE, INCTS, JPYPTRAN, MFUEL, OTHERNP, PCARMILE
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

    @mcp.tool()
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
