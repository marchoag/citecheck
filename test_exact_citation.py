#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('COURTLISTENER_API_KEY')

def test_exact_citation(citation):
    print(f"\n=== Testing Citation: {citation} ===")
    
    # Test 1: Quoted exact search
    url = 'https://www.courtlistener.com/api/rest/v4/search/'
    params = {
        'q': f'"{citation}"',
        'type': 'o',
        'format': 'json'
    }
    headers = {'Authorization': f'Token {api_key}'}
    
    response = requests.get(url, params=params, headers=headers)
    print(f'Status: {response.status_code}')
    print(f'URL: {response.url}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Count: {data.get("count", 0)}')
        
        if data.get('results'):
            for i, result in enumerate(data['results'][:5]):
                case_name = result.get('caseName', 'N/A')
                citations = []
                for c in result.get('citations', []):
                    vol = c.get('volume', '')
                    rep = c.get('reporter', '')
                    page = c.get('page', '')
                    if vol and rep and page:
                        citations.append(f"{vol} {rep} {page}")
                
                print(f'Result {i+1}: {case_name}')
                print(f'  Citations: {citations}')
                print(f'  Court: {result.get("court", "N/A")}')
                print(f'  Date: {result.get("dateFiled", "N/A")}')
                print()
        else:
            print("No results found!")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_exact_citation("410 US 113")
    test_exact_citation("347 US 483") 