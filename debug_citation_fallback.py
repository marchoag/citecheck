#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from citecheck import CitationChecker

load_dotenv()

def debug_citation_fallback():
    checker = CitationChecker()
    citation = "623 P.2d 268"
    
    print(f"=== Debugging Citation: {citation} ===")
    
    # Step 1: Check if it looks like citation format
    looks_like_citation = checker._looks_like_citation_format(citation)
    print(f"1. Looks like citation format: {looks_like_citation}")
    
    if looks_like_citation:
        # Step 2: Try Citation Lookup API
        print(f"\n2. Testing Citation Lookup API...")
        citation_result = checker._check_with_citation_api(citation)
        print(f"   Status: {citation_result['status']}")
        print(f"   Message: {citation_result['message']}")
        
        if citation_result['status'] == 'invalid':
            # Step 3: Try citation parts search
            print(f"\n3. Testing Citation Parts Fallback...")
            parsed_citation = checker._parse_citation_parts(citation)
            print(f"   Parsed citation: {parsed_citation}")
            
            if parsed_citation:
                fallback_result = checker._search_by_citation_parts(parsed_citation)
                print(f"   Fallback status: {fallback_result['status']}")
                print(f"   Fallback message: {fallback_result['message']}")
                if fallback_result['status'] == 'valid':
                    print(f"   Found {len(fallback_result['cases'])} case(s)")
                    for i, case in enumerate(fallback_result['cases'], 1):
                        print(f"     {i}. {case['name']}")
                        print(f"        Citation: {case.get('citation', 'N/A')}")

if __name__ == "__main__":
    debug_citation_fallback() 