#!/usr/bin/env python3
"""
Complete example: Create expense with v4 API
This example shows how to create a new expense entry with authentication and report lookup.
"""

import os
import requests
import base64
import json
from datetime import date
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()

    # Get credentials from environment
    client_id = os.getenv('CONCUR_CLIENT_ID')
    client_secret = os.getenv('CONCUR_CLIENT_SECRET')
    username = os.getenv('CONCUR_USERNAME')
    password = os.getenv('CONCUR_PASSWORD')

    if not all([client_id, client_secret, username, password]):
        print("❌ Missing required environment variables. Check your .env file.")
        return

    base_url = 'https://integration.api.concursolutions.com'

    try:
        # Step 1: Get access token
        print("🔐 Getting access token...")
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'password',
            'username': username,
            'password': password
        }

        token_response = requests.post(
            f'{base_url}/oauth2/v0/token',
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        token_response.raise_for_status()
        access_token = token_response.json()['access_token']
        print("✅ Access token obtained")

        # Step 2: Get user ID from JWT token
        token_parts = access_token.split('.')
        payload = json.loads(base64.urlsafe_b64decode(token_parts[1] + '==').decode('utf-8'))
        user_id = payload['sub']
        print(f"👤 User ID: {user_id}")

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        # Step 3: Get first available report
        print("\n📋 Getting available reports...")
        reports_response = requests.get(
            f'{base_url}/expensereports/v4/users/{user_id}/context/TRAVELER/reports?limit=1',
            headers=headers
        )
        reports_data = reports_response.json()
        if not reports_data.get('content'):
            print('❌ No reports found - create a report first')
            return

        report = reports_data['content'][0]
        # Try to extract report ID from different possible fields
        report_id = None
        if report.get('uri'):
            report_id = report['uri'].split('/')[-1]
        elif report.get('reportId'):
            report_id = report['reportId']
        elif report.get('id'):
            report_id = report['id']
        
        if not report_id:
            print('❌ Could not extract report ID from report data')
            print(f'Available fields: {list(report.keys())}')
            return
        print(f"✅ Using report: {report['name']} ({report_id})")

        # Step 4: Get first available expense type
        print("\n🏷️  Getting expense types...")
        exp_types_response = requests.get(
            f'{base_url}/expenseconfig/v4/users/{user_id}/context/TRAVELER/expensetypes',
            headers=headers
        )
        expense_types = exp_types_response.json()
        if not expense_types:
            print('❌ No expense types found')
            return

        expense_type = expense_types[0]  # Use first available type
        print(f"✅ Using expense type: {expense_type['name']} ({expense_type['expenseTypeId']})")

        # Step 5: Create expense
        print("\n💰 Creating expense...")
        expense_payload = {
            'expenseSource': 'EA',  # Always 'EA' for manually entered
            'exchangeRate': {
                'value': 1,
                'operation': 'MULTIPLY'
            },
            'expenseType': {
                'id': expense_type['expenseTypeId'],
                'name': expense_type['name'],
                'isDeleted': False,
                'listItemId': None
            },
            'transactionAmount': {
                'value': 25.50,
                'currencyCode': 'usd'  # lowercase for v4
            },
            'vendor': {
                'description': 'Business lunch vendor'  # vendor must be object with description
            },
            'transactionDate': date.today().strftime('%Y-%m-%d'),
            'businessPurpose': 'Client meeting lunch'  # simple string, not object
        }

        response = requests.post(
            f'{base_url}/expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses',
            headers=headers,
            json=expense_payload
        )

        if response.status_code in [200, 201]:
            print('✅ Expense created successfully!')
            print(f"   Amount: ${expense_payload['transactionAmount']['value']}")
            print(f"   Vendor: {expense_payload['vendor']['description']}")
            print(f"   Purpose: {expense_payload['businessPurpose']}")
            print(f"   Date: {expense_payload['transactionDate']}")
            print(f"   Type: {expense_type['name']}")
        else:
            print(f'❌ Error: {response.status_code} - {response.text}')
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except KeyError as e:
        print(f"❌ Missing field in response: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
