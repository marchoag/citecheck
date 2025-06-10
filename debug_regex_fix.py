#!/usr/bin/env python3

import re

def test_improved_patterns():
    test_citations = [
        "410 U.S. 113",
        "347 U.S. 483", 
        "623 P.2d 268",
        "123 F.3d 456",
        "410 US 113"
    ]
    
    # Improved patterns
    patterns = [
        (r'^\d+\s+[A-Za-z.]+\d+[a-z]*\s+\d+.*$', "Pattern 1: P.2d style"),
        (r'^\d+\s+[A-Za-z.]+\s+\d+.*$', "Pattern 2: U.S. style"),
        (r'^\d+\s+[A-Za-z]+\s+\d+.*$', "Pattern 3: US style"),
    ]
    
    for citation in test_citations:
        print(f"\nTesting: '{citation}'")
        for pattern, desc in patterns:
            match = re.match(pattern, citation.strip())
            print(f"  {desc}: {'✓' if match else '✗'}")
            
    # Test improved parsing patterns
    print("\n" + "="*50)
    print("PARSING TESTS:")
    
    parsing_patterns = [
        (r'(\d+)\s+([A-Za-z.]+\d+[a-z]*)\s+(\d+)', "P.2d/F.3d style"),  # "623 P.2d 268", "123 F.3d 456"
        (r'(\d+)\s+([A-Za-z.]+)\s+(\d+)', "U.S./US style"),             # "410 U.S. 113", "410 US 113"
    ]
    
    for citation in test_citations:
        print(f"\nParsing: '{citation}'")
        for pattern, desc in parsing_patterns:
            match = re.search(pattern, citation.strip())
            if match:
                volume, reporter, page = match.groups()
                print(f"  ✓ {desc}: Volume={volume}, Reporter='{reporter}', Page={page}")
                break
        else:
            print("  ✗ No pattern matched!")

if __name__ == "__main__":
    test_improved_patterns() 