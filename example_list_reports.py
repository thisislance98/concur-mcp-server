#!/usr/bin/env python3
"""
Complete example: List reports with v4 API
This example shows how to authenticate and list expense reports using Concur's v4 API.
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

        # Step 3: List reports
        print("\n📋 Listing reports...")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        params = {
            'limit': 10,
            'start': 0  # v4 uses 'start' instead of 'offset'
        }

        response = requests.get(
            f'{base_url}/expensereports/v4/users/{user_id}/context/TRAVELER/reports',
            headers=headers,
            params=params
        )

        if response.status_code == 200:
            data = response.json()
            reports = data.get('content', [])
            total_elements = data.get('totalElements', 0)
            
            print(f"✅ Found {len(reports)} reports (total: {total_elements})")
            print("\n📊 Reports:")
            
            for i, report in enumerate(reports, 1):
                total_amount = report.get('totalApprovedAmount', {})
                # Try to extract report ID from different possible fields
                report_id = 'N/A'
                if report.get('uri'):
                    report_id = report['uri'].split('/')[-1]
                elif report.get('reportId'):
                    report_id = report['reportId']
                elif report.get('id'):
                    report_id = report['id']
                amount = total_amount.get('value', 0)
                currency = total_amount.get('currencyCode', 'USD')
                
                print(f"  {i:2d}. {report['name']} ({report_id})")
                print(f"      Amount: {amount} {currency}")
                print(f"      Status: {report.get('approvalStatus', 'Unknown')}")
                print(f"      Created: {report.get('reportDate', 'Unknown')}")
                print()
                
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except KeyError as e:
        print(f"❌ Missing field in response: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
