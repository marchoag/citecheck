#!/usr/bin/env python3
"""
Debug script to examine CourtListener V4 API response structure
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def debug_api_response():
    api_key = os.getenv('COURTLISTENER_API_KEY')
    base_url = 'https://www.courtlistener.com/api/rest/v4/'
    headers = {
        'Authorization': f'Token {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Testing actual search query structure...")
    
    # Test the exact query that's failing
    params = {
        'case_name__icontains': 'Roe v. Wade',
        'citation__volume': '410',
        'citation__reporter': 'US', 
        'citation__page': '113',
        'page_size': 1
    }
    
    try:
        response = requests.get(f"{base_url}opinions/", headers=headers, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response type: {type(data)}")
                print("\n📋 Full Response Structure:")
                print(json.dumps(data, indent=2)[:1000] + "..." if len(json.dumps(data, indent=2)) > 1000 else json.dumps(data, indent=2))
                
                if isinstance(data, dict):
                    print(f"\n🔑 Top-level keys: {list(data.keys())}")
                    
                    if 'results' in data:
                        results = data['results']
                        print(f"Results type: {type(results)}")
                        print(f"Results count: {len(results) if hasattr(results, '__len__') else 'N/A'}")
                        
                        if results and len(results) > 0:
                            first_result = results[0]
                            print(f"\n📄 First result type: {type(first_result)}")
                            if isinstance(first_result, dict):
                                print(f"First result keys: {list(first_result.keys())}")
                            else:
                                print(f"First result content: {first_result}")
                        
            except json.JSONDecodeError:
                print("❌ Response is not valid JSON")
                print(f"Raw response: {response.text[:500]}")
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Also test a simpler query
    print("\n🔍 Testing simpler case name search...")
    simple_params = {
        'case_name__icontains': 'Roe',
        'page_size': 1
    }
    
    try:
        response = requests.get(f"{base_url}opinions/", headers=headers, params=simple_params)
        print(f"Simple search status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'count' in data:
                print(f"Total matches for 'Roe': {data['count']}")
            
    except Exception as e:
        print(f"❌ Simple search failed: {e}")

if __name__ == '__main__':
    debug_api_response() 