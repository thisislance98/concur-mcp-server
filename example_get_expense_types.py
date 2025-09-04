#!/usr/bin/env python3
"""
Complete example: Get expense types from v4 user-specific API
This example shows how to retrieve expense types available to the current user.
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

        # Step 3: Get expense types
        print("\n🏷️  Getting expense types...")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        response = requests.get(
            f'{base_url}/expenseconfig/v4/users/{user_id}/context/TRAVELER/expensetypes',
            headers=headers
        )

        if response.status_code == 200:
            expense_types = response.json()
            print(f"✅ Found {len(expense_types)} expense types for user")
            
            # Show available expense types
            user_types = []
            for et in expense_types:
                user_types.append({
                    'name': et['name'],
                    'id': et['expenseTypeId'],
                    'code': et['expenseCategoryCode']
                })
            
            print(f"\n📊 Available expense types ({len(user_types)}):")
            for i, et in enumerate(user_types[:15], 1):  # Show first 15
                print(f"  {i:2d}. ID: {et['id']}")
                print(f"      Name: {et['name']}")
                print(f"      Code: {et['code']}")
                print()
                
            if len(user_types) > 15:
                print(f"      ... and {len(user_types) - 15} more")
                
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
