#!/usr/bin/env python3
"""
Concur MCP Tools for v4 Expense Management
Provides tools for managing expense reports and entries using the v4-only SDK.
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


def _generate_v4_authentication_guide() -> Dict[str, Any]:
    """Generate v4 authentication and setup guide."""
    return {
        "title": "Concur v4 API Authentication Setup",
        "overview": "Learn how to authenticate with Concur v4 APIs using OAuth2 password grant flow.",
        "how_to": {
            "steps": [
                {
                    "step": 1,
                    "title": "Set up credentials",
                    "description": "Gather your Concur API credentials from your administrator",
                    "code": "# Required credentials for v4 APIs\nclient_id = 'your_client_id'\nclient_secret = 'your_client_secret'\nusername = 'your_concur_username'\npassword = 'your_concur_password'\n\n# v4 API endpoints\nbase_url = 'https://integration.api.concursolutions.com'\ntoken_url = f'{base_url}/oauth2/v0/token'"
                },
                {
                    "step": 2,
                    "title": "Get access token",
                    "description": "Make OAuth2 token request to get bearer token for v4 APIs",
                    "code": "import requests\n\n# Token request payload\ntoken_data = {\n    'client_id': client_id,\n    'client_secret': client_secret,\n    'grant_type': 'password',\n    'username': username,\n    'password': password\n}\n\nheaders = {'Content-Type': 'application/x-www-form-urlencoded'}\n\nresponse = requests.post(token_url, data=token_data, headers=headers)\nresponse.raise_for_status()\n\ntoken_data = response.json()\naccess_token = token_data['access_token']\nexpires_in = token_data.get('expires_in', 3600)\n\nprint(f'v4 Token obtained, expires in {expires_in} seconds')"
                },
                {
                    "step": 3,
                    "title": "Test v4 connection",
                    "description": "Verify token works with v4 endpoints",
                    "code": "# Test v4 API call - list reports\napi_headers = {\n    'Authorization': f'Bearer {access_token}',\n    'Accept': 'application/json'\n}\n\n# Get user ID first (required for v4 endpoints)\nuser_response = requests.get(\n    f'{base_url}/profile/v1/me',\n    headers=api_headers\n)\nuser_id = user_response.json().get('sub')\n\n# Test v4 reports endpoint\ntest_response = requests.get(\n    f'{base_url}/expensereports/v4/users/{user_id}/context/TRAVELER/reports?limit=1',\n    headers=api_headers\n)\n\nif test_response.status_code == 200:\n    print('v4 Authentication successful!')\n    reports = test_response.json()\n    print(f'Found {len(reports.get(\"content\", []))} reports')\nelse:\n    print(f'v4 Authentication failed: {test_response.status_code}')"
                }
            ]
        },
        "v4_features": {
            "user_context": "All v4 endpoints require user ID in the path",
            "response_format": "v4 uses different response structures with 'content' arrays",
            "endpoint_patterns": "v4 endpoints follow /service/v4/users/{userId}/context/TRAVELER/ pattern",
            "payload_structures": "v4 uses different JSON payload formats for create/update operations"
        },
        "api_endpoints": {
            "token_url": "https://integration.api.concursolutions.com/oauth2/v0/token",
            "user_profile": "https://integration.api.concursolutions.com/profile/v1/me",
            "reports_v4": "https://integration.api.concursolutions.com/expensereports/v4/users/{userId}/context/TRAVELER/reports",
            "expenses_v4": "https://integration.api.concursolutions.com/expensereports/v4/users/{userId}/context/TRAVELER/reports/{reportId}/expenses"
        }
    }


def _generate_v4_reports_guide() -> Dict[str, Any]:
    """Generate v4 reports management guide."""
    return {
        "title": "Managing Expense Reports with v4 APIs",
        "overview": "Learn how to create, list, and delete expense reports using v4 endpoints with proper user context.",
        "how_to": {
            "steps": [
                {
                    "step": 1,
                    "title": "List existing reports (v4)",
                    "description": "Get reports using v4 endpoint structure with user context",
                    "code": "# List reports with v4 API\nimport requests\n\n# Assuming you have access_token and user_id from authentication\nheaders = {\n    'Authorization': f'Bearer {access_token}',\n    'Accept': 'application/json'\n}\n\nparams = {\n    'limit': 10,\n    'start': 0  # v4 uses 'start' instead of 'offset'\n}\n\nresponse = requests.get(\n    f'https://integration.api.concursolutions.com/expensereports/v4/users/{user_id}/context/TRAVELER/reports',\n    headers=headers,\n    params=params\n)\n\nif response.status_code == 200:\n    data = response.json()\n    reports = data.get('content', [])\n    print(f'Found {len(reports)} reports (total: {data.get(\"totalElements\", 0)})')\n    \n    for report in reports:\n        total_amount = report.get('totalApprovedAmount', {})\n        print(f'  {report[\"name\"]}: {total_amount.get(\"value\", 0)} {total_amount.get(\"currencyCode\", \"USD\")}')\nelse:\n    print(f'Error: {response.status_code} - {response.text}')"
                },
                {
                    "step": 2,
                    "title": "Create new report (v4)",
                    "description": "Create a report using v4 payload structure",
                    "code": "# Create new report with v4 API\nreport_payload = {\n    'name': 'Business Trip - January 2024',\n    'purpose': 'Client meetings and conference attendance',\n    'businessPurpose': 'Sales meetings with key clients in San Francisco',\n    'currencyCode': 'USD',\n    'country': 'US'\n}\n\nresponse = requests.post(\n    f'https://integration.api.concursolutions.com/expensereports/v4/users/{user_id}/context/TRAVELER/reports',\n    headers=headers,\n    json=report_payload\n)\n\nif response.status_code in [200, 201]:\n    report_data = response.json()\n    # Extract report ID from URI\n    report_uri = report_data.get('uri', '')\n    report_id = report_uri.split('/')[-1] if report_uri else None\n    print(f'Created report: {report_id}')\n    print(f'URI: {report_uri}')\nelse:\n    print(f'Error: {response.status_code} - {response.text}')"
                },
                {
                    "step": 3,
                    "title": "Delete report (v4)",
                    "description": "Delete an empty report using v4 endpoint",
                    "code": "# Delete report with v4 API\nreport_id = 'your_report_id'\n\nresponse = requests.delete(\n    f'https://integration.api.concursolutions.com/expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}',\n    headers=headers\n)\n\nif response.status_code in [200, 204]:\n    print('Report deleted successfully')\nelse:\n    print(f'Delete failed: {response.status_code} - {response.text}')"
                }
            ]
        },
        "v4_differences": {
            "response_structure": "v4 uses 'content' array with pagination info (totalElements, totalPages)",
            "field_names": "Different field names (e.g., 'name' instead of 'Name', camelCase)",
            "uri_extraction": "Report ID must be extracted from 'uri' field in create response",
            "pagination": "Uses 'start' parameter instead of 'offset'",
            "user_context": "All endpoints require /users/{userId}/context/TRAVELER/ path"
        },
        "examples": [
            {
                "title": "Complete Report Workflow",
                "description": "Create, populate, and manage a report lifecycle",
                "code": "# Complete report workflow example\nimport requests\nfrom datetime import date\n\n# 1. Create report\nreport_data = {\n    'name': f'Expense Report - {date.today()}',\n    'purpose': 'Business travel expenses',\n    'businessPurpose': 'Client meetings and project work',\n    'currencyCode': 'USD',\n    'country': 'US'\n}\n\ncreate_response = requests.post(\n    f'https://integration.api.concursolutions.com/expensereports/v4/users/{user_id}/context/TRAVELER/reports',\n    headers=headers,\n    json=report_data\n)\n\nif create_response.status_code in [200, 201]:\n    report_uri = create_response.json().get('uri')\n    report_id = report_uri.split('/')[-1]\n    print(f'✅ Created report: {report_id}')\n    \n    # 2. List reports to verify\n    list_response = requests.get(\n        f'https://integration.api.concursolutions.com/expensereports/v4/users/{user_id}/context/TRAVELER/reports?limit=5',\n        headers=headers\n    )\n    \n    if list_response.status_code == 200:\n        reports = list_response.json().get('content', [])\n        print(f'✅ Found {len(reports)} reports')\n        \n        # Find our new report\n        our_report = next((r for r in reports if report_id in r.get('uri', '')), None)\n        if our_report:\n            print(f'✅ Verified report exists: {our_report[\"name\"]}')\n    \n    # 3. Delete report (if needed)\n    # delete_response = requests.delete(\n    #     f'https://integration.api.concursolutions.com/expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}',\n    #     headers=headers\n    # )\n    # print(f'Delete status: {delete_response.status_code}')\n    \nelse:\n    print(f'❌ Failed to create report: {create_response.status_code}')"
            }
        ]
    }


def _generate_v4_expenses_guide() -> Dict[str, Any]:
    """Generate v4 expenses management guide."""
    return {
        "title": "Managing Expenses with v4 APIs",
        "overview": "Learn how to create, update, and manage expense entries using v4 endpoints with proper payload structures.",
        "how_to": {
            "steps": [
                {
                    "step": 1,
                    "title": "Get expense types (v4)",
                    "description": "Retrieve user-specific expense types using v4 endpoint",
                    "code": "# Get expense types from v4 user-specific API\nimport requests\n\nheaders = {\n    'Authorization': f'Bearer {access_token}',\n    'Accept': 'application/json'\n}\n\nresponse = requests.get(\n    f'https://integration.api.concursolutions.com/expenseconfig/v4/users/{user_id}/context/TRAVELER/expensetypes',\n    headers=headers\n)\n\nif response.status_code == 200:\n    expense_types = response.json()\n    print(f'Found {len(expense_types)} expense types for user')\n    \n    # Filter out system types (starting with '0')\n    user_types = []\n    for et in expense_types:\n        if not et['expenseTypeId'].startswith('0'):\n            user_types.append({\n                'name': et['name'],\n                'id': et['expenseTypeId'],\n                'code': et['expenseCategoryCode']\n            })\n    \n    print(f'Available user expense types: {len(user_types)}')\n    for et in user_types[:5]:  # Show first 5\n        print(f\"  {et['id']}: {et['name']} ({et['code']})\")\nelse:\n    print(f'Error: {response.status_code} - {response.text}')"
                },
                {
                    "step": 2,
                    "title": "Create expense (v4)",
                    "description": "Add expense using v4 payload structure",
                    "code": "# Create expense with v4 API\nreport_id = 'your_report_id'\nexpense_type_id = 'your_expense_type_id'\nexpense_type_name = 'your_expense_type_name'\n\nexpense_payload = {\n    'expenseSource': 'EA',  # Always 'EA' for manually entered\n    'exchangeRate': {\n        'value': 1,\n        'operation': 'MULTIPLY'\n    },\n    'expenseType': {\n        'id': expense_type_id,\n        'name': expense_type_name,\n        'isDeleted': False,\n        'listItemId': None\n    },\n    'transactionAmount': {\n        'value': 25.50,\n        'currencyCode': 'usd'  # lowercase for v4\n    },\n    'vendor': {\n        'description': 'Business lunch vendor'\n    },\n    'transactionDate': '2024-01-15'\n}\n\n# Add business purpose if provided\nbusiness_purpose = 'Client meeting lunch'\nif business_purpose:\n    expense_payload['businessPurpose'] = {\n        'value': business_purpose\n    }\n\nresponse = requests.post(\n    f'https://integration.api.concursolutions.com/expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses',\n    headers=headers,\n    json=expense_payload\n)\n\nif response.status_code in [200, 201]:\n    print('✅ Expense created successfully')\nelse:\n    print(f'❌ Error: {response.status_code} - {response.text}')"
                },
                {
                    "step": 3,
                    "title": "Update expense (v4)",
                    "description": "Update expense using v4 PATCH endpoint",
                    "code": "# Update expense with v4 API\nexpense_id = 'your_expense_id'\n\n# Build update payload with only fields to change\nupdate_payload = {\n    'expenseSource': 'EA',\n    'exchangeRate': {\n        'value': 1,\n        'operation': 'MULTIPLY'\n    }\n}\n\n# Add fields to update\nnew_amount = 35.00\nif new_amount:\n    update_payload['transactionAmount'] = {\n        'value': new_amount,\n        'currencyCode': 'usd'\n    }\n\nnew_vendor = 'Updated Restaurant Name'\nif new_vendor:\n    update_payload['vendor'] = {\n        'description': new_vendor\n    }\n\nnew_date = '2024-01-16'\nif new_date:\n    update_payload['transactionDate'] = new_date\n\nresponse = requests.patch(\n    f'https://integration.api.concursolutions.com/expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses/{expense_id}',\n    headers=headers,\n    json=update_payload\n)\n\nif response.status_code in [200, 204]:\n    print('✅ Expense updated successfully')\nelse:\n    print(f'❌ Update failed: {response.status_code} - {response.text}')"
                },
                {
                    "step": 4,
                    "title": "Delete expense (v4)",
                    "description": "Delete expense using v4 endpoint",
                    "code": "# Delete expense with v4 API\nresponse = requests.delete(\n    f'https://integration.api.concursolutions.com/expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses/{expense_id}',\n    headers=headers\n)\n\nif response.status_code in [200, 204]:\n    print('✅ Expense deleted successfully')\nelse:\n    print(f'❌ Delete failed: {response.status_code} - {response.text}')"
                }
            ]
        },
        "v4_payload_structure": {
            "required_fields": ["expenseSource", "exchangeRate", "expenseType", "transactionAmount"],
            "expense_source": "Always use 'EA' for manually entered expenses",
            "exchange_rate": "Always use {'value': 1, 'operation': 'MULTIPLY'} for base currency",
            "expense_type": "Must include id, name, isDeleted: false, listItemId: null",
            "transaction_amount": "Use 'value' and 'currencyCode' (lowercase)",
            "optional_fields": ["vendor", "businessPurpose", "transactionDate"],
            "field_formats": {
                "vendor": "Object with 'description' field: {'description': 'vendor name'}",
                "businessPurpose": "Simple string value, NOT an object",
                "transactionDate": "String in YYYY-MM-DD format"
            }
        },
        "examples": [
            {
                "title": "Complete Expense Workflow",
                "description": "End-to-end expense management with error handling",
                "code": "# Complete expense workflow with error handling\nimport requests\nfrom datetime import date\n\ndef create_expense_workflow(report_id, amount, description, vendor_name):\n    \"\"\"Complete expense creation workflow.\"\"\"\n    \n    # 1. Get expense types first\n    types_response = requests.get(\n        f'https://integration.api.concursolutions.com/expenseconfig/v4/users/{user_id}/context/TRAVELER/expensetypes',\n        headers=headers\n    )\n    \n    if types_response.status_code != 200:\n        return {'success': False, 'error': 'Failed to get expense types'}\n    \n    # Find a suitable expense type\n    expense_types = types_response.json()\n    suitable_type = None\n    \n    for et in expense_types:\n        if not et['expenseTypeId'].startswith('0'):  # Skip system types\n            suitable_type = et\n            break\n    \n    if not suitable_type:\n        return {'success': False, 'error': 'No suitable expense type found'}\n    \n    print(f'Using expense type: {suitable_type[\"name\"]}')\n    \n    # 2. Create expense\n    expense_payload = {\n        'expenseSource': 'EA',\n        'exchangeRate': {'value': 1, 'operation': 'MULTIPLY'},\n        'expenseType': {\n            'id': suitable_type['expenseTypeId'],\n            'name': suitable_type['name'],\n            'isDeleted': False,\n            'listItemId': None\n        },\n        'transactionAmount': {\n            'value': amount,\n            'currencyCode': 'usd'\n        },\n        'vendor': {'description': vendor_name},\n        'transactionDate': date.today().strftime('%Y-%m-%d')\n    }\n    \n    if description:\n        expense_payload['businessPurpose'] = {'value': description}\n    \n    create_response = requests.post(\n        f'https://integration.api.concursolutions.com/expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses',\n        headers=headers,\n        json=expense_payload\n    )\n    \n    if create_response.status_code in [200, 201]:\n        print(f'✅ Created expense: ${amount} at {vendor_name}')\n        return {'success': True, 'message': 'Expense created successfully'}\n    else:\n        print(f'❌ Failed to create expense: {create_response.status_code}')\n        return {'success': False, 'error': create_response.text}\n\n# Example usage\nresult = create_expense_workflow(\n    report_id='your_report_id',\n    amount=42.50,\n    description='Business lunch with client',\n    vendor_name='Downtown Bistro'\n)\n\nprint(f'Workflow result: {result}')"
            }
        ]
    }


def _generate_v4_error_handling_guide() -> Dict[str, Any]:
    """Generate v4 error handling guide."""
    return {
        "title": "v4 API Error Handling and Troubleshooting",
        "overview": "Learn how to handle common v4 API errors and implement robust error handling patterns.",
        "common_errors": {
            "authentication": {
                "401_unauthorized": {
                    "description": "Token expired or invalid",
                    "solution": "Refresh access token using OAuth2 flow",
                    "code": "# Handle 401 errors\nif response.status_code == 401:\n    print('Token expired, refreshing...')\n    # Re-authenticate and retry\n    new_token = get_new_access_token()\n    headers['Authorization'] = f'Bearer {new_token}'\n    response = requests.get(url, headers=headers)"
                },
                "403_forbidden": {
                    "description": "Insufficient permissions or user context issues",
                    "solution": "Verify user has access to the resource and correct user ID",
                    "code": "# Handle 403 errors\nif response.status_code == 403:\n    print('Access denied - check user permissions')\n    # Verify user ID and permissions\n    user_response = requests.get(f'{base_url}/profile/v1/me', headers=headers)\n    user_data = user_response.json()\n    print(f'Current user: {user_data.get(\"sub\")}')"
                }
            },
            "validation": {
                "400_bad_request": {
                    "description": "Invalid payload structure or missing required fields",
                    "solution": "Validate payload against v4 schema requirements",
                    "code": "# Handle 400 errors with payload validation\nif response.status_code == 400:\n    error_data = response.json() if response.content else {}\n    print(f'Validation error: {error_data}')\n    \n    # Check required v4 fields\n    required_fields = ['expenseSource', 'exchangeRate', 'expenseType', 'transactionAmount']\n    for field in required_fields:\n        if field not in payload:\n            print(f'Missing required field: {field}')"
                },
                "422_unprocessable": {
                    "description": "Data validation failed (e.g., invalid expense type)",
                    "solution": "Verify expense types are valid for the user",
                    "code": "# Handle 422 errors\nif response.status_code == 422:\n    print('Data validation failed')\n    # Re-fetch valid expense types\n    types_response = requests.get(\n        f'{base_url}/expenseconfig/v4/users/{user_id}/context/TRAVELER/expensetypes',\n        headers=headers\n    )\n    valid_types = [et['expenseTypeId'] for et in types_response.json()]"
                }
            },
            "not_found": {
                "404_not_found": {
                    "description": "Report or expense not found",
                    "solution": "Verify resource IDs and user access",
                    "code": "# Handle 404 errors\nif response.status_code == 404:\n    print('Resource not found')\n    # Verify report exists and user has access\n    reports_response = requests.get(\n        f'{base_url}/expensereports/v4/users/{user_id}/context/TRAVELER/reports',\n        headers=headers\n    )\n    report_ids = [r.get('uri', '').split('/')[-1] for r in reports_response.json().get('content', [])]"
                }
            }
        },
        "best_practices": {
            "retry_logic": {
                "description": "Implement exponential backoff for transient errors",
                "code": "import time\nimport random\n\ndef make_request_with_retry(url, headers, payload=None, max_retries=3):\n    \"\"\"Make API request with exponential backoff retry logic.\"\"\"\n    \n    for attempt in range(max_retries):\n        try:\n            if payload:\n                response = requests.post(url, headers=headers, json=payload)\n            else:\n                response = requests.get(url, headers=headers)\n            \n            # Success cases\n            if response.status_code in [200, 201, 204]:\n                return response\n            \n            # Permanent errors - don't retry\n            if response.status_code in [400, 401, 403, 404]:\n                return response\n            \n            # Transient errors - retry with backoff\n            if response.status_code in [429, 500, 502, 503, 504]:\n                if attempt < max_retries - 1:\n                    wait_time = (2 ** attempt) + random.uniform(0, 1)\n                    print(f'Retrying in {wait_time:.1f} seconds...')\n                    time.sleep(wait_time)\n                    continue\n            \n            return response\n            \n        except requests.exceptions.RequestException as e:\n            if attempt < max_retries - 1:\n                wait_time = (2 ** attempt) + random.uniform(0, 1)\n                print(f'Request exception, retrying in {wait_time:.1f} seconds...')\n                time.sleep(wait_time)\n                continue\n            raise e\n    \n    return response"
            },
            "validation": {
                "description": "Validate data before sending to API",
                "code": "def validate_expense_payload(payload):\n    \"\"\"Validate v4 expense payload before sending.\"\"\"\n    errors = []\n    \n    # Required fields\n    required = ['expenseSource', 'exchangeRate', 'expenseType', 'transactionAmount']\n    for field in required:\n        if field not in payload:\n            errors.append(f'Missing required field: {field}')\n    \n    # Validate expense source\n    if payload.get('expenseSource') != 'EA':\n        errors.append('expenseSource must be \"EA\" for manual entries')\n    \n    # Validate exchange rate structure\n    exchange_rate = payload.get('exchangeRate', {})\n    if not (exchange_rate.get('value') == 1 and exchange_rate.get('operation') == 'MULTIPLY'):\n        errors.append('exchangeRate must be {\"value\": 1, \"operation\": \"MULTIPLY\"}')\n    \n    # Validate expense type structure\n    expense_type = payload.get('expenseType', {})\n    required_et_fields = ['id', 'name', 'isDeleted']\n    for field in required_et_fields:\n        if field not in expense_type:\n            errors.append(f'expenseType missing field: {field}')\n    \n    # Validate transaction amount\n    trans_amount = payload.get('transactionAmount', {})\n    if not trans_amount.get('value') or not trans_amount.get('currencyCode'):\n        errors.append('transactionAmount must have value and currencyCode')\n    \n    return errors"
            }
        }
    }


def _generate_v4_best_practices_guide() -> Dict[str, Any]:
    """Generate v4 best practices guide."""
    return {
        "title": "v4 API Best Practices and Optimization",
        "overview": "Learn best practices for efficient and reliable v4 API usage.",
        "performance": {
            "pagination": {
                "description": "Use proper pagination for large datasets",
                "code": "def get_all_reports(user_id, headers):\n    \"\"\"Get all reports with proper pagination.\"\"\"\n    all_reports = []\n    start = 0\n    limit = 50  # Reasonable batch size\n    \n    while True:\n        params = {'limit': limit, 'start': start}\n        response = requests.get(\n            f'{base_url}/expensereports/v4/users/{user_id}/context/TRAVELER/reports',\n            headers=headers,\n            params=params\n        )\n        \n        if response.status_code != 200:\n            break\n            \n        data = response.json()\n        reports = data.get('content', [])\n        \n        if not reports:\n            break\n            \n        all_reports.extend(reports)\n        \n        # Check if we have more pages\n        if len(reports) < limit or start + len(reports) >= data.get('totalElements', 0):\n            break\n            \n        start += limit\n    \n    return all_reports"
            },
            "batch_operations": {
                "description": "Batch multiple operations efficiently",
                "code": "import concurrent.futures\nimport threading\n\nclass ConcurV4Client:\n    def __init__(self, access_token, user_id):\n        self.headers = {\n            'Authorization': f'Bearer {access_token}',\n            'Accept': 'application/json',\n            'Content-Type': 'application/json'\n        }\n        self.user_id = user_id\n        self.base_url = 'https://integration.api.concursolutions.com'\n    \n    def create_multiple_expenses(self, report_id, expenses_data):\n        \"\"\"Create multiple expenses with controlled concurrency.\"\"\"\n        results = []\n        \n        def create_single_expense(expense_data):\n            try:\n                response = requests.post(\n                    f'{self.base_url}/expensereports/v4/users/{self.user_id}/context/TRAVELER/reports/{report_id}/expenses',\n                    headers=self.headers,\n                    json=expense_data\n                )\n                return {\n                    'success': response.status_code in [200, 201],\n                    'status_code': response.status_code,\n                    'data': expense_data\n                }\n            except Exception as e:\n                return {\n                    'success': False,\n                    'error': str(e),\n                    'data': expense_data\n                }\n        \n        # Use ThreadPoolExecutor with limited workers to avoid overwhelming API\n        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:\n            future_to_expense = {executor.submit(create_single_expense, expense): expense \n                               for expense in expenses_data}\n            \n            for future in concurrent.futures.as_completed(future_to_expense):\n                result = future.result()\n                results.append(result)\n        \n        return results"
            }
        },
        "security": {
            "token_management": {
                "description": "Secure token handling and refresh",
                "code": "class SecureTokenManager:\n    def __init__(self, client_id, client_secret, username, password):\n        self.client_id = client_id\n        self.client_secret = client_secret\n        self.username = username\n        self.password = password\n        self.token_url = 'https://integration.api.concursolutions.com/oauth2/v0/token'\n        self._token_data = None\n        self._token_expiry = None\n        self._lock = threading.Lock()\n    \n    def get_access_token(self):\n        \"\"\"Get valid access token with automatic refresh.\"\"\"\n        with self._lock:\n            # Check if current token is still valid\n            if (self._token_data and self._token_expiry and \n                datetime.now() < self._token_expiry - timedelta(minutes=5)):  # 5 min buffer\n                return self._token_data['access_token']\n            \n            # Refresh token\n            return self._refresh_token()\n    \n    def _refresh_token(self):\n        \"\"\"Refresh access token.\"\"\"\n        payload = {\n            'client_id': self.client_id,\n            'client_secret': self.client_secret,\n            'grant_type': 'password',\n            'username': self.username,\n            'password': self.password\n        }\n        \n        response = requests.post(\n            self.token_url,\n            data=payload,\n            headers={'Content-Type': 'application/x-www-form-urlencoded'}\n        )\n        \n        if response.status_code == 200:\n            self._token_data = response.json()\n            expires_in = self._token_data.get('expires_in', 3600)\n            self._token_expiry = datetime.now() + timedelta(seconds=expires_in)\n            return self._token_data['access_token']\n        else:\n            raise Exception(f'Token refresh failed: {response.status_code}')"
            }
        },
        "monitoring": {
            "logging": {
                "description": "Comprehensive logging for debugging",
                "code": "import logging\nimport json\nfrom datetime import datetime\n\n# Configure logging\nlogging.basicConfig(\n    level=logging.INFO,\n    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',\n    handlers=[\n        logging.FileHandler('concur_v4_api.log'),\n        logging.StreamHandler()\n    ]\n)\n\nlogger = logging.getLogger('ConcurV4API')\n\ndef log_api_request(method, url, payload=None, response=None):\n    \"\"\"Log API requests and responses for debugging.\"\"\"\n    request_data = {\n        'timestamp': datetime.now().isoformat(),\n        'method': method,\n        'url': url,\n        'payload_size': len(json.dumps(payload)) if payload else 0\n    }\n    \n    if response:\n        request_data.update({\n            'status_code': response.status_code,\n            'response_size': len(response.content) if response.content else 0,\n            'response_time_ms': getattr(response, 'elapsed', timedelta()).total_seconds() * 1000\n        })\n    \n    logger.info(f'API Request: {json.dumps(request_data)}')\n    \n    if response and response.status_code >= 400:\n        logger.error(f'API Error: {response.status_code} - {response.text[:500]}')\n\n# Usage example\nresponse = requests.post(url, headers=headers, json=payload)\nlog_api_request('POST', url, payload, response)"
            }
        }
    }


def create_expense_tools(mcp, concur_sdk: ConcurExpenseSDK):
    """Add expense-related tools to the MCP server for v4-only SDK."""
    
    @mcp.tool()
    def get_concur_api_guide(
        topic: ConcurAPITopic,
        include_examples: bool = True,
        include_howto: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive Concur v4 API guide with direct API call examples and how-to instructions.
        
        The examples show v4 HTTP requests using Python requests library.
        All guides are updated for v4 endpoints and payload structures.
        
        Available Topics:
        - AUTHENTICATION: OAuth2 setup and token management for v4 APIs
        - REPORTS: Creating, listing, and deleting expense reports with v4 endpoints
        - EXPENSES: Managing expense entries (create, update, delete) with v4 payload structures
        - ERROR_HANDLING: Common v4 API errors and troubleshooting patterns
        - BEST_PRACTICES: Performance optimization, security, and monitoring for v4 APIs
        
        Args:
            topic: The API topic to get guidance for (see Available Topics above)
            include_examples: Whether to include code examples (default: True)
            include_howto: Whether to include step-by-step how-to instructions (default: True)
        
        Returns:
            Comprehensive v4 guide with examples, how-tos, and reference information
        """
        try:
            # Map topics to their v4 content generators
            topic_generators = {
                ConcurAPITopic.AUTHENTICATION: _generate_v4_authentication_guide,
                ConcurAPITopic.SETUP: _generate_v4_authentication_guide,  # Same as auth
                ConcurAPITopic.REPORTS: _generate_v4_reports_guide,
                ConcurAPITopic.EXPENSES: _generate_v4_expenses_guide,
                ConcurAPITopic.ERROR_HANDLING: _generate_v4_error_handling_guide,
                ConcurAPITopic.BEST_PRACTICES: _generate_v4_best_practices_guide,
            }
            
            # Get the appropriate generator
            generator = topic_generators.get(topic)
            if not generator:
                return {
                    'success': False,
                    'error': f'v4 Documentation not yet available for topic: {topic.value}',
                    'available_topics': [t.value for t in topic_generators.keys()],
                    'message': f'Topic {topic.value} is not implemented yet. Available v4 topics: {", ".join([t.value for t in topic_generators.keys()])}'
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
                'api_version': 'v4',
                **guide_content,
                'message': f'Retrieved v4 guide for {topic.value}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to generate v4 guide for {topic.value}: {str(e)}'
            }
    
    @mcp.tool()
    def test_concur_connection() -> Dict[str, Any]:
        """
        Test the connection to Concur v4 APIs.
        
        Returns:
            Dictionary indicating connection status and API version
        """
        try:
            result = concur_sdk.test_connection()
            if result['success']:
                result['api_version'] = 'v4'
                result['message'] = f"Successfully connected to Concur v4 APIs. {result.get('message', '')}"
            return result
            
        except (AuthenticationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Failed to connect to Concur v4 APIs: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Unexpected error testing v4 connection: {str(e)}"
            }
    
    @mcp.tool()
    def list_concur_reports(limit: int = 25, user: Optional[str] = None) -> Dict[str, Any]:
        """
        List expense reports using v4 API.
        
        Args:
            limit: Maximum number of reports to return (default: 25)
            user: Optional user ID (default: current authenticated user)
        
        Returns:
            Dictionary containing reports and v4 metadata
        """
        try:
            result = concur_sdk.list_reports(limit=limit, user=user)
            if result['success']:
                result['api_version'] = 'v4'
                result['message'] = f"Successfully retrieved {result['count']} reports using v4 API"
            return result
            
        except (AuthenticationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Failed to retrieve reports from v4 API: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Unexpected error retrieving reports: {str(e)}"
            }

    @mcp.tool()
    def create_concur_report(name: str, purpose: str = "", business_purpose: str = "", 
                           currency_code: str = "USD", country: str = "US") -> Dict[str, Any]:
        """
        Create a new expense report using v4 API.
        
        Args:
            name: Name of the report
            purpose: Purpose of the report
            business_purpose: Business justification for the report
            currency_code: Currency code (default: USD)
            country: Country code (default: US)
        
        Returns:
            Dictionary containing created report details from v4 API
        """
        try:
            result = concur_sdk.create_report(
                name=name,
                purpose=purpose,
                business_purpose=business_purpose,
                currency_code=currency_code,
                country=country
            )
            if result['success']:
                result['api_version'] = 'v4'
                result['message'] = f"Successfully created report '{name}' using v4 API"
            return result
            
        except (AuthenticationError, ValidationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Failed to create report using v4 API: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Unexpected error creating report: {str(e)}"
            }

    @mcp.tool()
    def delete_concur_report(report_id: str) -> Dict[str, Any]:
        """
        Delete an expense report using v4 API.
        
        Args:
            report_id: The ID of the report to delete
        
        Returns:
            Dictionary indicating success/failure
        """
        try:
            result = concur_sdk.delete_report(report_id)
            if result['success']:
                result['api_version'] = 'v4'
                result['message'] = f"Successfully deleted report {report_id} using v4 API"
            return result
            
        except NotFoundError:
            return {
                'success': False,
                'error': 'Report not found',
                'api_version': 'v4',
                'message': f"No report found with ID: {report_id}"
            }
        except (AuthenticationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Failed to delete report using v4 API: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Unexpected error deleting report: {str(e)}"
            }

    @mcp.tool()
    def list_concur_expenses(report_id: str, limit: int = 25, offset: int = 0) -> Dict[str, Any]:
        """
        List expense entries for a specific report using v4 API.
        
        Args:
            report_id: The ID of the report
            limit: Maximum number of expenses to return (default: 25)
            offset: Number of records to skip (default: 0)
        
        Returns:
            Dictionary containing expenses and v4 metadata
        """
        try:
            result = concur_sdk.list_expenses(report_id=report_id, limit=limit, offset=offset)
            if result['success']:
                result['api_version'] = 'v4'
                result['message'] = f"Successfully retrieved {result['count']} expenses for report {report_id} using v4 API"
            return result
            
        except NotFoundError:
            return {
                'success': False,
                'error': 'Report not found',
                'api_version': 'v4',
                'message': f"No report found with ID: {report_id}"
            }
        except (AuthenticationError, ValidationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Failed to retrieve expenses using v4 API: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Unexpected error retrieving expenses: {str(e)}"
            }

    @mcp.tool()
    def create_concur_expense(report_id: str, expense_type: str, amount: float, 
                             currency_code: str = "USD", transaction_date: Optional[str] = None,
                             business_purpose: str = "", vendor_description: str = "") -> Dict[str, Any]:
        """
        Create a new expense entry using v4 API.
        
        Args:
            report_id: The ID of the report to add the expense to
            expense_type: Expense type ID from get_concur_expense_types
            amount: Transaction amount
            currency_code: Currency code (default: USD)
            transaction_date: Date of transaction in YYYY-MM-DD format (default: today)
            business_purpose: Business purpose of the expense
            vendor_description: Vendor/merchant description
        
        Returns:
            Dictionary containing created expense details from v4 API
        """
        try:
            result = concur_sdk.create_expense(
                report_id=report_id,
                expense_type=expense_type,
                amount=amount,
                currency_code=currency_code,
                transaction_date=transaction_date,
                business_purpose=business_purpose,
                vendor_description=vendor_description
            )
            if result['success']:
                result['api_version'] = 'v4'
                result['message'] = f"Successfully created expense of {amount} {currency_code} using v4 API"
            return result
            
        except NotFoundError:
            return {
                'success': False,
                'error': 'Report not found',
                'api_version': 'v4',
                'message': f"No report found with ID: {report_id}"
            }
        except (AuthenticationError, ValidationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Failed to create expense using v4 API: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Unexpected error creating expense: {str(e)}"
            }

    @mcp.tool()
    def update_concur_expense(expense_id: str, report_id: str, amount: Optional[float] = None,
                             expense_type: Optional[str] = None, currency_code: Optional[str] = None,
                             transaction_date: Optional[str] = None, business_purpose: Optional[str] = None,
                             vendor_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing expense entry using v4 API.
        
        Args:
            expense_id: The ID of the expense entry to update
            report_id: The ID of the report containing the expense
            amount: New transaction amount (optional)
            expense_type: New expense type ID (optional)
            currency_code: New currency code (optional)
            transaction_date: New transaction date in YYYY-MM-DD format (optional)
            business_purpose: New business purpose (optional)
            vendor_description: New vendor description (optional)
        
        Returns:
            Dictionary indicating success/failure from v4 API
        """
        try:
            # Build kwargs with only non-None values
            kwargs = {}
            if amount is not None:
                kwargs['amount'] = amount
            if expense_type is not None:
                kwargs['expense_type'] = expense_type
            if currency_code is not None:
                kwargs['currency_code'] = currency_code
            if transaction_date is not None:
                kwargs['transaction_date'] = transaction_date
            if business_purpose is not None:
                kwargs['business_purpose'] = business_purpose
            if vendor_description is not None:
                kwargs['vendor_description'] = vendor_description
            
            if not kwargs:
                return {
                    'success': False,
                    'error': 'No fields to update',
                    'api_version': 'v4',
                    'message': 'At least one field must be provided for update'
                }
            
            result = concur_sdk.update_expense(expense_id, report_id, **kwargs)
            if result['success']:
                result['api_version'] = 'v4'
                result['message'] = f"Successfully updated expense {expense_id} using v4 API"
            return result
            
        except NotFoundError:
            return {
                'success': False,
                'error': 'Expense not found',
                'api_version': 'v4',
                'message': f"No expense found with ID: {expense_id}"
            }
        except (AuthenticationError, ValidationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Failed to update expense using v4 API: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Unexpected error updating expense: {str(e)}"
            }

    @mcp.tool()
    def delete_concur_expense(expense_id: str, report_id: str) -> Dict[str, Any]:
        """
        Delete an expense entry using v4 API.
        
        Args:
            expense_id: The ID of the expense entry to delete
            report_id: The ID of the report containing the expense
        
        Returns:
            Dictionary indicating success/failure from v4 API
        """
        try:
            result = concur_sdk.delete_expense(expense_id, report_id)
            if result['success']:
                result['api_version'] = 'v4'
                result['message'] = f"Successfully deleted expense {expense_id} using v4 API"
            return result
            
        except NotFoundError:
            return {
                'success': False,
                'error': 'Expense not found',
                'api_version': 'v4',
                'message': f"No expense found with ID: {expense_id}"
            }
        except (AuthenticationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Failed to delete expense using v4 API: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Unexpected error deleting expense: {str(e)}"
            }

    @mcp.tool()
    def get_concur_expense_types() -> Dict[str, Any]:
        """
        Get available expense types using v4 user-specific API.
        
        This function retrieves expense types that are available to the current user,
        using the v4 user-specific endpoint that filters out system types.
        
        Returns:
            Dictionary containing user-specific expense types from v4 API
        """
        try:
            result = concur_sdk.get_expense_types()
            if result['success']:
                result['api_version'] = 'v4'
                result['endpoint'] = 'user-specific v4 expense types'
                result['message'] = f"Successfully retrieved {result.get('count', 0)} expense types using v4 API"
            return result
            
        except (AuthenticationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Failed to retrieve expense types from v4 API: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Unexpected error retrieving expense types: {str(e)}"
            }

    @mcp.tool()
    def get_concur_payment_types() -> Dict[str, Any]:
        """
        Get available payment types using v4 API.
        
        Returns:
            Dictionary containing payment types from v4 API
        """
        try:
            result = concur_sdk.get_payment_types()
            if result['success']:
                result['api_version'] = 'v4'
                result['message'] = f"Successfully retrieved {result.get('count', 0)} payment types using v4 API"
            return result
            
        except (AuthenticationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Failed to retrieve payment types from v4 API: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Unexpected error retrieving payment types: {str(e)}"
            }

    @mcp.tool()
    def get_concur_user_id() -> Dict[str, Any]:
        """
        Get the current user's ID from the v4 API.
        
        Returns:
            Dictionary containing the user ID
        """
        try:
            user_id = concur_sdk.get_user_id()
            if user_id:
                return {
                    'success': True,
                    'user_id': user_id,
                    'api_version': 'v4',
                    'message': f"Successfully retrieved user ID: {user_id}"
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not determine user ID',
                    'api_version': 'v4',
                    'message': 'Failed to extract user ID from authentication token'
                }
            
        except (AuthenticationError, ConcurAPIError) as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Failed to get user ID from v4 API: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_version': 'v4',
                'message': f"Unexpected error getting user ID: {str(e)}"
            }
