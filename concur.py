import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Required environment variables
client_id = os.getenv("CONCUR_CLIENT_ID")
client_secret = os.getenv("CONCUR_CLIENT_SECRET")
username = os.getenv("CONCUR_USERNAME")
password = os.getenv("CONCUR_PASSWORD")

def missing_vars():
    return [
        var for var, val in [
            ("CONCUR_CLIENT_ID", client_id),
            ("CONCUR_CLIENT_SECRET", client_secret),
            ("CONCUR_USERNAME", username),
            ("CONCUR_PASSWORD", password),
        ] if not val
    ]

if missing_vars():
    sys.exit(f"Missing required environment variables: {', '.join(missing_vars())}")

# Concur OAuth2 token endpoint (US instance)
TOKEN_URL = "https://integration.api.concursolutions.com/oauth2/v0/token"

payload = {
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "password",
    "username": username,
    "password": password,
}
headers = {"Content-Type": "application/x-www-form-urlencoded"}

try:
    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    access_token = data["access_token"]
    print(f"Full JWT token: {access_token}")
except requests.RequestException as e:
    print(f"Error requesting token: {e}")
    if e.response is not None:
        print(e.response.text)
    sys.exit(1)

print("JWT token retrieved successfully!")
sys.exit(0) 