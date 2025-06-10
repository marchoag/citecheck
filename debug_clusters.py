#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('COURTLISTENER_API_KEY')

def debug_clusters_response():
    headers = {'Authorization': f'Token {api_key}'}
    
    # Test 1: Try clusters endpoint with specific citation
    print("=== Testing Clusters Endpoint for 410 US 113 ===")
    url = 'https://www.courtlistener.com/api/rest/v4/clusters/'
    params = {
        'citation__volume': '410',
        'citation__reporter': 'U.S.',
        'citation__page': '113',
        'format': 'json'
    }
    
    response = requests.get(url, params=params, headers=headers)
    print(f'Status: {response.status_code}')
    print(f'URL: {response.url}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Raw response type: {type(data)}')
        print(f'Raw response keys: {data.keys() if isinstance(data, dict) else "Not a dict"}')
        print(f'Response (first 500 chars): {str(data)[:500]}...')
        
        # Print full JSON structure
        print("\n=== FULL JSON RESPONSE ===")
        print(json.dumps(data, indent=2)[:2000] + "..." if len(str(data)) > 2000 else json.dumps(data, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    debug_clusters_response() 