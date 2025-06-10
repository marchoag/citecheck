#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('COURTLISTENER_API_KEY')

def test_citation_endpoints():
    headers = {'Authorization': f'Token {api_key}'}
    
    # Test 1: Try the citations endpoint directly
    print("=== Testing Citations Endpoint ===")
    url = 'https://www.courtlistener.com/api/rest/v4/citations/'
    params = {
        'volume': '410',
        'reporter': 'US',
        'page': '113'
    }
    
    response = requests.get(url, params=params, headers=headers)
    print(f'Status: {response.status_code}')
    print(f'URL: {response.url}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Count: {data.get("count", 0)}')
        for result in data.get('results', [])[:3]:
            print(f'Citation ID: {result.get("id")}')
            print(f'Citation: {result.get("volume")} {result.get("reporter")} {result.get("page")}')
            print(f'Cluster: {result.get("cluster")}')
            print()
    else:
        print(f"Error: {response.text}")
    
    # Test 2: Try clusters endpoint
    print("=== Testing Clusters Endpoint ===")
    url = 'https://www.courtlistener.com/api/rest/v4/clusters/'
    params = {
        'citation__volume': '410',
        'citation__reporter': 'US', 
        'citation__page': '113'
    }
    
    response = requests.get(url, params=params, headers=headers)
    print(f'Status: {response.status_code}')
    print(f'URL: {response.url}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Count: {data.get("count", 0)}')
        for result in data.get('results', [])[:3]:
            print(f'Case: {result.get("case_name", "N/A")}')
            print(f'Court: {result.get("docket", {}).get("court", "N/A")}')
            print(f'Date: {result.get("date_filed", "N/A")}')
            print(f'Citations: {result.get("citations", [])}')
            print()
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_citation_endpoints() 