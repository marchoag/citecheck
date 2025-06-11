#!/usr/bin/env python3
"""
Debug script to test CourtListener API connection
"""

import os
import requests
from dotenv import load_dotenv
import json

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

def test_courtlistener_api():
    """Test what CourtListener returns for Roe v Wade to debug the precedential_status issue"""
    
    # Get API key from user
    api_key = input("Enter your CourtListener API key: ")
    headers = {'Authorization': f'Token {api_key}'}
    url = 'https://www.courtlistener.com/api/rest/v4/search/'

    # Test 1: No filter
    params1 = {'q': 'caseName:(Roe v. Wade)', 'format': 'json'}
    print('\n=== TEST 1: No precedential_status filter ===')
    try:
        r1 = requests.get(url, headers=headers, params=params1)
        if r1.status_code == 200:
            data1 = r1.json()
            results1 = data1.get('results', [])
            print(f'Found {len(results1)} results')
            if results1:
                first = results1[0]
                print(f'First result: {first.get("caseName", "Unknown")}')
                print('\nKeys available:')
                for key in sorted(first.keys()):
                    if 'precedent' in key.lower() or 'status' in key.lower() or 'published' in key.lower():
                        print(f'  ★ {key}: {first[key]}')
                    else:
                        print(f'    {key}: {first[key]}')
                        
                # Test with Published filter
                print('\n=== TEST 2: With precedential_status=Published ===')
                params2 = {'q': 'caseName:(Roe v. Wade)', 'precedential_status': 'Published', 'format': 'json'}
                r2 = requests.get(url, headers=headers, params=params2)
                if r2.status_code == 200:
                    data2 = r2.json()
                    results2 = data2.get('results', [])
                    print(f'Found {len(results2)} results with Published filter')
                else:
                    print(f'Published filter failed: {r2.status_code} - {r2.text}')
                    
                # Test different precedential_status values
                print('\n=== TEST 3: Testing different precedential_status values ===')
                for status_val in ['Published', 'published', 'Precedential', 'precedential']:
                    params3 = {'q': 'caseName:(Roe v. Wade)', 'precedential_status': status_val, 'format': 'json'}
                    r3 = requests.get(url, headers=headers, params=params3)
                    if r3.status_code == 200:
                        data3 = r3.json()
                        results3 = data3.get('results', [])
                        print(f'  {status_val}: {len(results3)} results')
                    else:
                        print(f'  {status_val}: ERROR {r3.status_code}')
        else:
            print(f'Error: {r1.status_code} - {r1.text}')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_api_connection() 
    test_courtlistener_api() 