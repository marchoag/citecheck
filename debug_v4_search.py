#!/usr/bin/env python3
"""
Debug V4 API search behavior more thoroughly
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def debug_v4_search():
    api_key = os.getenv('COURTLISTENER_API_KEY')
    base_url = 'https://www.courtlistener.com/api/rest/v4/'
    headers = {
        'Authorization': f'Token {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Deep dive into V4 API search behavior...")
    
    # Test 1: Search clusters with exact case name
    print("\n1. Testing clusters with exact case name:")
    params = {'case_name': 'Roe v. Wade', 'page_size': 5}
    test_and_show_results(base_url, headers, 'clusters/', params)
    
    # Test 2: Search clusters with different variations
    print("\n2. Testing clusters with 'Roe':")
    params = {'case_name__contains': 'Roe', 'page_size': 5}
    test_and_show_results(base_url, headers, 'clusters/', params)
    
    # Test 3: Try citation search on clusters
    print("\n3. Testing clusters with citation:")
    params = {'citation': '410 US 113', 'page_size': 5}
    test_and_show_results(base_url, headers, 'clusters/', params)
    
    # Test 4: Search for a known case with different approach
    print("\n4. Testing search without filters (recent cases):")
    params = {'page_size': 5, 'ordering': '-date_created'}
    test_and_show_results(base_url, headers, 'clusters/', params)
    
    # Test 5: Try text search
    print("\n5. Testing text search for 'abortion':")
    params = {'q': 'abortion', 'page_size': 5}
    test_and_show_results(base_url, headers, 'search/', params)

def test_and_show_results(base_url, headers, endpoint, params):
    try:
        print(f"   URL: {base_url}{endpoint}")
        print(f"   Params: {params}")
        
        response = requests.get(f"{base_url}{endpoint}", headers=headers, params=params)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"   Results: {len(results)}")
            
            for i, result in enumerate(results[:3]):
                if endpoint == 'clusters/':
                    case_name = result.get('case_name', 'No case name')
                    date = result.get('date_filed', result.get('date_created', 'No date'))
                    court = result.get('court', 'No court')
                    print(f"     {i+1}. {case_name} | {court} | {date}")
                    
                    # Show citations if available
                    citations = result.get('citations', [])
                    if citations:
                        for cit in citations[:2]:
                            vol = cit.get('volume', '')
                            rep = cit.get('reporter', '')
                            page = cit.get('page', '')
                            print(f"        Citation: {vol} {rep} {page}")
                elif endpoint == 'search/':
                    snippet = result.get('snippet', 'No snippet')[:100]
                    print(f"     {i+1}. {snippet}...")
                else:
                    print(f"     {i+1}. {result}")
        else:
            print(f"   Error: {response.status_code} - {response.text[:200]}")
            
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == '__main__':
    debug_v4_search() 