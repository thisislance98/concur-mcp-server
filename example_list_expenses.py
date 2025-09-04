#!/usr/bin/env python3
"""
Complete example: List expenses for a report using v4 API
This example shows how to list all expenses in a specific report.
"""

import os
import requests
import base64
import json
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
            'Accept': 'application/json'
        }

        # Step 3: Get first available report
        print("\n📋 Getting available reports...")
        reports_response = requests.get(
            f'{base_url}/expensereports/v4/users/{user_id}/context/TRAVELER/reports?limit=1',
            headers=headers
        )
        reports_data = reports_response.json()
        if not reports_data.get('content'):
            print('❌ No reports found')
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

        # Step 4: List expenses in the report
        print("\n💰 Listing expenses...")
        expenses_response = requests.get(
            f'{base_url}/expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses',
            headers=headers
        )

        if expenses_response.status_code == 200:
            expenses = expenses_response.json()
            if isinstance(expenses, list):
                print(f"✅ Found {len(expenses)} expenses in report")
                
                if expenses:
                    print("\n📊 Expenses:")
                    for i, expense in enumerate(expenses, 1):
                        # Handle different response formats
                        expense_id = expense.get('expenseId', 'N/A')
                        expense_type = expense.get('expenseType', {})
                        transaction_amount = expense.get('transactionAmount', {})
                        vendor = expense.get('vendor', {})
                        
                        print(f"  {i:2d}. ID: {expense_id}")
                        print(f"      Type: {expense_type.get('name', 'Unknown')}")
                        print(f"      Amount: {transaction_amount.get('value', 0)} {transaction_amount.get('currencyCode', 'USD')}")
                        print(f"      Vendor: {vendor.get('description', 'N/A')}")
                        print(f"      Date: {expense.get('transactionDate', 'N/A')}")
                        
                        # Handle businessPurpose as either string or object
                        business_purpose = expense.get('businessPurpose')
                        if isinstance(business_purpose, dict):
                            business_purpose = business_purpose.get('value', 'N/A')
                        elif not business_purpose:
                            business_purpose = 'N/A'
                        print(f"      Purpose: {business_purpose}")
                        print()
                else:
                    print("📝 No expenses found in this report")
            else:
                print(f"❌ Unexpected response format: {type(expenses)}")
        else:
            print(f'❌ Error: {expenses_response.status_code} - {expenses_response.text}')
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except KeyError as e:
        print(f"❌ Missing field in response: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
