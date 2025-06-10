#!/usr/bin/env python3

import re

def test_regex_patterns():
    test_citations = [
        "410 U.S. 113",
        "347 U.S. 483", 
        "623 P.2d 268",
        "123 F.3d 456",
        "410 US 113"
    ]
    
    patterns = [
        (r'^\d+\s+[A-Za-z.]+\s+\d+[a-z]*\s+\d+.*$', "Pattern 1: 623 P.2d 268"),
        (r'^\d+\s+[A-Za-z.]+\s*\d*\s+\d+.*$', "Pattern 2: 410 US 113"),
    ]
    
    for citation in test_citations:
        print(f"\nTesting: '{citation}'")
        for pattern, desc in patterns:
            match = re.match(pattern, citation.strip())
            print(f"  {desc}: {'✓' if match else '✗'}")
            
        # Test parsing too
        parsing_patterns = [
            r'(\d+)\s+([A-Za-z.]+\s+\d+[a-z]*)\s+(\d+)',        # "623 P.2d 268", "123 F.3d 456"
            r'(\d+)\s+([A-Za-z.]+(?:\s+[A-Za-z.]+)*?)\s+(\d+)',  # "410 U.S. 113"
            r'(\d+)\s+([A-Za-z.]+)\s+(\d+)',                     # "410 US 113"
        ]
        
        print("  Parsing:")
        for i, pattern in enumerate(parsing_patterns, 1):
            match = re.search(pattern, citation.strip())
            if match:
                volume, reporter, page = match.groups()
                print(f"    Pattern {i}: Volume={volume}, Reporter='{reporter}', Page={page}")
                break
        else:
            print("    No pattern matched!")

if __name__ == "__main__":
    test_regex_patterns() 