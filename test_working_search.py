#!/usr/bin/env python3
"""
Test different search approaches to find a working method
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_different_approaches():
    api_key = os.getenv('COURTLISTENER_API_KEY')
    headers = {'Authorization': f'Token {api_key}'}
    
    print("🔍 Testing different search approaches...")
    
    # Test 1: Maybe there's a search endpoint that works
    print("\n1. Testing /search/ endpoint with direct query:")
    try:
        url = "https://www.courtlistener.com/api/rest/v4/search/"
        params = {'q': 'Roe v Wade', 'type': 'o', 'page_size': 3}  # 'o' for opinions
        response = requests.get(url, headers=headers, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Results: {len(data.get('results', []))}")
            for result in data.get('results', [])[:2]:
                print(f"  - {result.get('caseName', 'No case name')}")
        else:
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 2: Try browsable API approach
    print("\n2. Testing browse by specific endpoint:")
    try:
        # Look for a case by browsing through well-known cases
        url = "https://www.courtlistener.com/api/rest/v4/clusters/"
        params = {'court__jurisdiction': 'F', 'page_size': 5}  # Federal cases
        response = requests.get(url, headers=headers, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Federal cases found: {len(data.get('results', []))}")
            for result in data.get('results', [])[:3]:
                print(f"  - {result.get('case_name', 'No name')} ({result.get('date_filed', 'No date')})")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 3: Check if pagination is the issue
    print("\n3. Testing basic clusters with no filters:")
    try:
        url = "https://www.courtlistener.com/api/rest/v4/clusters/"
        params = {'page_size': 3}
        response = requests.get(url, headers=headers, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"Basic results: {len(results)}")
            
            # Check if all results are actually the same
            unique_cases = set()
            for result in results:
                case_name = result.get('case_name', 'No name')
                unique_cases.add(case_name)
            
            print(f"Unique case names: {len(unique_cases)}")
            print(f"Cases: {list(unique_cases)[:5]}")
            
            if len(unique_cases) == 1:
                print("⚠️  ALL RESULTS ARE THE SAME CASE! This indicates an API issue.")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == '__main__':
    test_different_approaches() 