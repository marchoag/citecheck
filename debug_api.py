#!/usr/bin/env python3
"""
Debug script to test CourtListener API connection
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_api_connection():
    api_key = os.getenv('COURTLISTENER_API_KEY')
    
    # Check if API key is loaded
    if not api_key:
        print("❌ No API key found in environment variables")
        print("Make sure COURTLISTENER_API_KEY is set in your .env file")
        return
    
    if api_key == "YOUR_PLACEHOLDER_API_KEY_HERE":
        print("❌ API key is still the placeholder value")
        print("Please replace it with your real CourtListener API key in .env")
        return
    
    print(f"✅ API key found (length: {len(api_key)} characters)")
    print(f"✅ API key starts with: {api_key[:8]}...")
    
    # Test basic API connection
    base_url = 'https://www.courtlistener.com/api/rest/v4/'
    headers = {
        'Authorization': f'Token {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("\n🔍 Testing API connection...")
    
    # Try a simple endpoint first
    try:
        response = requests.get(f"{base_url}courts/", headers=headers, params={'page_size': 1})
        print(f"Courts endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API connection successful!")
        elif response.status_code == 403:
            print("❌ 403 Forbidden - API key might be invalid")
            print("Check that your API key is correct in the .env file")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Test opinions endpoint
    print("\n🔍 Testing opinions endpoint...")
    try:
        response = requests.get(
            f"{base_url}opinions/", 
            headers=headers, 
            params={'page_size': 1}
        )
        print(f"Opinions endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data.get('count', 0)} total opinions in database")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == '__main__':
    test_api_connection() 