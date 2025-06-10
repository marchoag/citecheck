#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('COURTLISTENER_API_KEY')

def test_citation_lookup():
    """Test the citation lookup endpoint that Mike recommended"""
    headers = {'Authorization': f'Token {api_key}'}
    
    # Test the citation lookup endpoint for Roe v. Wade (410 U.S. 113)
    print("=== Testing Citation Lookup Endpoint for 410 U.S. 113 ===")
    url = 'https://www.courtlistener.com/api/rest/v4/citation-lookup/'
    
    # Use POST method with 'text' parameter as shown in the documentation
    data = {
        'text': 'Roe v. Wade (410 U.S. 113) established reproductive rights.'
    }
    
    response = requests.post(url, data=data, headers=headers)
    print(f'Status: {response.status_code}')
    print(f'URL: {response.url}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Response type: {type(data)}')
        
        # Print the full response in a readable format
        print("\n=== FULL JSON RESPONSE ===")
        print(json.dumps(data, indent=2))
        
        # Extract key information if available
        if isinstance(data, list) and len(data) > 0:
            print(f"\n=== CITATIONS FOUND ===")
            for i, citation_result in enumerate(data):
                print(f"\nCitation {i+1}:")
                if 'citation' in citation_result:
                    print(f"  Citation: {citation_result['citation']}")
                if 'normalized_citations' in citation_result:
                    print(f"  Normalized: {citation_result['normalized_citations']}")
                if 'status' in citation_result:
                    print(f"  Status: {citation_result['status']}")
                if 'clusters' in citation_result and citation_result['clusters']:
                    cluster = citation_result['clusters'][0]
                    if 'case_name' in cluster:
                        print(f"  Case Name: {cluster['case_name']}")
                    if 'date_filed' in cluster:
                        print(f"  Date Filed: {cluster['date_filed']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_alternative_texts():
    """Test different text formats with citations"""
    headers = {'Authorization': f'Token {api_key}'}
    
    test_texts = [
        'The case 410 U.S. 113 was decided by the Supreme Court.',
        'In Roe v. Wade, 410 US 113 (1973), the Court ruled...',
        'See 410 U.S. 113 for more details.',
        'Brown v. Board, 347 U.S. 483 (1954) ended segregation.'
    ]
    
    for text in test_texts:
        print(f"\n=== Testing Text: '{text}' ===")
        url = 'https://www.courtlistener.com/api/rest/v4/citation-lookup/'
        data = {'text': text}
        
        response = requests.post(url, data=data, headers=headers)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list):
                print(f"Found {len(result)} citations")
                for citation in result:
                    if 'citation' in citation:
                        print(f"  Citation: {citation['citation']}")
                        if 'status' in citation:
                            print(f"  Status: {citation['status']}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    test_citation_lookup()
    test_alternative_texts() 