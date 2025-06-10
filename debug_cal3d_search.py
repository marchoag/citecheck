#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('COURTLISTENER_API_KEY')

def debug_cal3d_search():
    headers = {'Authorization': f'Token {api_key}'}
    
    citation_parts = {'volume': '10', 'reporter': 'Cal.3d', 'page': '616', 'original': '10 Cal.3d 616'}
    
    # Test different query formats
    query_tests = [
        f"citation.volume:{citation_parts['volume']} AND citation.reporter:{citation_parts['reporter']} AND citation.page:{citation_parts['page']}",
        f"citation.volume:10 AND citation.reporter:Cal.3d AND citation.page:616",
        f'citation.volume:10 AND citation.reporter:"Cal.3d" AND citation.page:616',
        f'citation.volume:10 AND citation.reporter:"Cal. 3d" AND citation.page:616',
        f'citation:"10 Cal.3d 616"',
        f'citation:"10 Cal. 3d 616"'
    ]
    
    for i, query in enumerate(query_tests, 1):
        print(f"\n=== Test {i}: {query} ===")
        
        params = {
            'q': query,
            'order_by': 'dateFiled desc',
            'format': 'json'
        }
        
        response = requests.get('https://www.courtlistener.com/api/rest/v4/search/', headers=headers, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"Found {len(results)} results")
            
            if results:
                for j, result in enumerate(results[:2], 1):
                    print(f"  {j}. {result.get('caseName', 'Unknown')}")
                    print(f"     Date: {result.get('dateFiled', 'Unknown')}")
                    print(f"     Citations: {result.get('citation', [])}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    debug_cal3d_search() 