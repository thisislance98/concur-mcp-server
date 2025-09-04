#!/usr/bin/env python3
"""
Complete example: Create new report with v4 API
This example shows how to create a new expense report using Concur's v4 API.
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

        # Step 3: Get user's default policy (required for v4 API)
        print("\n🔍 Getting user policies...")
        policies_response = requests.get(
            f'{base_url}/expenseconfig/v4/users/{user_id}/context/TRAVELER/policies',
            headers=headers
        )
        
        if policies_response.status_code != 200:
            print(f"❌ Error getting policies: {policies_response.status_code} - {policies_response.text}")
            return
        
        policies = policies_response.json()
        default_policy_id = None
        
        for policy in policies:
            if policy.get('isDefault', False):
                default_policy_id = policy.get('policyId') or policy.get('id')
                print(f"✅ Found default policy: {policy.get('policyName', 'Unknown')} ({default_policy_id})")
                break
        
        if not default_policy_id and policies:
            # Use first available policy if no default found
            default_policy_id = policies[0].get('policyId') or policies[0].get('id')
            print(f"⚠️  No default policy, using first available: {default_policy_id}")
        
        if not default_policy_id:
            print("❌ No policies found")
            return

        # Step 4: Create new report
        print("\n📋 Creating new report...")
        from datetime import datetime
        
        # Use v4 payload format with required policyId
        report_payload = {
            'name': f'Business Trip - {date.today().strftime("%Y-%m-%d")}',
            'reportDate': datetime.now().strftime('%Y-%m-%d'),
            'businessPurpose': 'Sales meetings with key clients in San Francisco',
            'policyId': default_policy_id  # Required in v4 API
        }

        response = requests.post(
            f'{base_url}/expensereports/v4/users/{user_id}/context/TRAVELER/reports',
            headers=headers,
            json=report_payload
        )

        if response.status_code in [200, 201]:
            report_data = response.json()
            # Extract report ID from URI
            report_uri = report_data.get('uri', '')
            report_id = report_uri.split('/')[-1] if report_uri else None
            
            print('✅ Report created successfully!')
            print(f"   Name: {report_payload['name']}")
            print(f"   Report ID: {report_id}")
            print(f"   URI: {report_uri}")
            print(f"   Report Date: {report_payload['reportDate']}")
            print(f"   Business Purpose: {report_payload['businessPurpose']}")
            print(f"   Policy ID: {report_payload['policyId']}")
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
