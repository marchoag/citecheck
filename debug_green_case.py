#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from citecheck import CitationChecker

load_dotenv()

def debug_green_case():
    checker = CitationChecker()
    
    print("=== Testing Green v. Superior Court Case ===")
    
    # Test 1: Case name search
    print("\n1. Testing case name: 'Green v. Superior Court'")
    result1 = checker.check_citation("Green v. Superior Court")
    print(f"Status: {result1['status']}")
    print(f"Method: {result1.get('method', 'Unknown')}")
    if result1.get('cases'):
        print(f"Found {len(result1['cases'])} case(s):")
        for i, case in enumerate(result1['cases'], 1):
            print(f"  {i}. {case['name']}")
            print(f"     Date: {case.get('date', 'Unknown')}")
            print(f"     Citation: {case.get('citation', case.get('citations', 'N/A'))}")
    
    print("\n" + "="*50)
    
    # Test 2: Citation search
    print("\n2. Testing citation: '10 Cal.3d 616'")
    
    # First check if it recognizes the format
    looks_like_citation = checker._looks_like_citation_format("10 Cal.3d 616")
    print(f"Looks like citation format: {looks_like_citation}")
    
    # Parse the citation
    parsed = checker._parse_citation_parts("10 Cal.3d 616")
    print(f"Parsed citation: {parsed}")
    
    # Try the full check
    result2 = checker.check_citation("10 Cal.3d 616")
    print(f"Status: {result2['status']}")
    print(f"Method: {result2.get('method', 'Unknown')}")
    print(f"Message: {result2.get('message', 'No message')}")
    if result2.get('cases'):
        print(f"Found {len(result2['cases'])} case(s):")
        for i, case in enumerate(result2['cases'], 1):
            print(f"  {i}. {case['name']}")
            print(f"     Date: {case.get('date', 'Unknown')}")
            print(f"     Citation: {case.get('citation', case.get('citations', 'N/A'))}")

if __name__ == "__main__":
    debug_green_case() 