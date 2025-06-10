#!/usr/bin/env python3
"""
Debug script to test V4 API search parameters
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_search_parameters():
    api_key = os.getenv('COURTLISTENER_API_KEY')
    base_url = 'https://www.courtlistener.com/api/rest/v4/'
    headers = {
        'Authorization': f'Token {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Testing different search approaches for 'Roe v. Wade'...")
    
    # Test 1: Our current approach
    print("\n1. Testing current search parameters:")
    params1 = {
        'case_name__icontains': 'Roe v. Wade',
        'citation__volume': '410',
        'citation__reporter': 'US',
        'citation__page': '113',
        'page_size': 3
    }
    print(f"Parameters: {params1}")
    test_search(base_url, headers, 'opinions/', params1)
    
    # Test 2: Just case name
    print("\n2. Testing just case name:")
    params2 = {
        'case_name__icontains': 'Roe v. Wade',
        'page_size': 3
    }
    print(f"Parameters: {params2}")
    test_search(base_url, headers, 'opinions/', params2)
    
    # Test 3: Try different case name variations
    print("\n3. Testing case name 'Roe':")
    params3 = {
        'case_name__icontains': 'Roe',
        'page_size': 3
    }
    print(f"Parameters: {params3}")
    test_search(base_url, headers, 'opinions/', params3)
    
    # Test 4: Check if we should search clusters instead
    print("\n4. Testing clusters endpoint:")
    params4 = {
        'case_name__icontains': 'Roe v. Wade',
        'page_size': 3
    }
    print(f"Parameters: {params4}")
    test_search(base_url, headers, 'clusters/', params4)
    
    # Test 5: Check available search fields
    print("\n5. Getting schema info...")
    try:
        response = requests.get(f"{base_url}opinions/schema/", headers=headers)
        if response.status_code == 200:
            schema = response.json()
            if 'fields' in schema:
                print("Available opinion fields:")
                for field_name in sorted(schema['fields'].keys()):
                    print(f"  - {field_name}")
        else:
            print(f"Schema request failed: {response.status_code}")
    except:
        print("Could not fetch schema")

def test_search(base_url, headers, endpoint, params):
    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 'unknown')
            results = data.get('results', [])
            
            print(f"Count: {count}")
            print(f"Results returned: {len(results)}")
            
            if results:
                for i, result in enumerate(results[:2]):  # Show first 2 results
                    if endpoint == 'clusters/':
                        case_name = result.get('case_name', 'Unknown')
                        date = result.get('date_filed', 'Unknown')
                        print(f"  Result {i+1}: {case_name} ({date})")
                    else:
                        cluster_id = result.get('cluster_id', 'Unknown')
                        date = result.get('date_created', 'Unknown')
                        print(f"  Result {i+1}: Cluster {cluster_id} ({date})")
        else:
            print(f"Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == '__main__':
    test_search_parameters() 