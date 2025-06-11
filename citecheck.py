#!/usr/bin/env python3
"""
Citation Checker CLI Tool
Check legal citations using the CourtListener API v4
"""

import os
import sys
import requests
import click
import re
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from difflib import SequenceMatcher

# Load environment variables
load_dotenv()

class CitationChecker:
    def __init__(self, api_key=None):
        # Use provided API key or fall back to environment variable
        self.api_key = api_key or os.getenv('COURTLISTENER_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required - either pass it as parameter or set COURTLISTENER_API_KEY environment variable")
        
        self.citation_lookup_url = "https://www.courtlistener.com/api/rest/v4/citation-lookup/"
        self.search_url = "https://www.courtlistener.com/api/rest/v4/search/"
        self.headers = {
            'Authorization': f'Token {self.api_key}',
            'User-Agent': 'CiteCheck/2.0'
        }
    
    def check_citation(self, citation_text, include_unpublished=False):
        """
        Enhanced citation checking using multiple CourtListener APIs.
        Handles both case names and citation formats.
        
        Args:
            citation_text (str): The citation or case name to search for
            include_unpublished (bool): Whether to include unpublished opinions (default: False)
        """
        citation_text = citation_text.strip()
        
        # First, try the Citation Lookup API if it looks like a citation format
        if self._looks_like_citation_format(citation_text):
            citation_result = self._check_with_citation_api(citation_text, include_unpublished)
            if citation_result['status'] == 'valid':
                return citation_result
            elif citation_result['status'] == 'invalid':
                # Citation Lookup API couldn't find it - try targeted citation search
                parsed_citation = self._parse_citation_parts(citation_text)
                if parsed_citation:
                    fallback_result = self._search_by_citation_parts(parsed_citation, include_unpublished)
                    if fallback_result['status'] == 'valid':
                        return fallback_result
                # If targeted search also fails, return the original citation lookup result
                return citation_result
            else:
                # API error - continue with fallbacks
                pass
        
        # If Citation API failed or this looks like a case name, use enhanced search
        if self._looks_like_case_name(citation_text):
            return self._enhanced_case_name_search(citation_text, include_unpublished)
        else:
            # Try parsing as citation and search for case name
            parsed_citation = self._parse_citation_parts(citation_text)
            if parsed_citation:
                return self._search_by_citation_parts(parsed_citation, include_unpublished)
            else:
                # Fall back to text search with warning
                result = self._enhanced_case_name_search(citation_text, include_unpublished)
                if result['status'] == 'invalid':
                    result['message'] = f'No cases found for "{citation_text}". Try entering a case name (like "Smith v. Jones") or a proper citation (like "410 U.S. 113").'
                return result
    
    def _check_with_citation_api(self, citation_text, include_unpublished=False):
        """
        Use the CourtListener Citation Lookup API to validate and parse citations.
        This is the most accurate method for citation validation.
        """
        try:
            # The Citation Lookup API expects POST with 'text' parameter
            data = {
                'text': citation_text
            }
            
            response = requests.post(
                self.citation_lookup_url, 
                headers=self.headers, 
                data=data  # Use data, not json
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # The Citation Lookup API returns a list of found citations
                if isinstance(result, list) and len(result) > 0:
                    cases = []
                    for citation_result in result:
                        if citation_result.get('status') == 200 and citation_result.get('clusters'):
                            # Get the first cluster (case) for each citation
                            for cluster in citation_result['clusters']:
                                # Get the primary/official citation only
                                primary_citation = self._get_primary_citation(cluster.get('citations', []))
                                
                                # Get publication status from cluster
                                precedential_status = cluster.get('precedential_status', 'unknown')
                                court_name = cluster.get('docket', {}).get('court', 'Unknown') if isinstance(cluster.get('docket'), dict) else 'Unknown'
                                is_published = self._is_published_status(precedential_status, court_name)
                                
                                # Filter out unpublished cases if not requested
                                if not include_unpublished and not is_published:
                                    continue
                                
                                case_info = {
                                    'name': cluster.get('case_name', 'Unknown'),
                                    'court': cluster.get('docket', {}).get('court', 'Unknown') if isinstance(cluster.get('docket'), dict) else 'Unknown',
                                    'date': cluster.get('date_filed', 'Unknown'),
                                    'citation': primary_citation,  # Single primary citation instead of list
                                    'absolute_url': cluster.get('absolute_url', ''),
                                    'citation_count': cluster.get('citation_count', 0),
                                    'slug': cluster.get('slug', ''),
                                    'found_citation': citation_result.get('citation', ''),
                                    'normalized_citation': citation_result.get('normalized_citations', []),
                                    'publication_status': precedential_status,
                                    'is_published': is_published
                                }
                                cases.append(case_info)
                    
                    if cases:
                        return {
                            'status': 'valid',
                            'message': f'Valid citation found: {citation_text}',
                            'search_type': 'citation_lookup',
                            'cases': cases,
                            'total_results': len(cases),
                            'method': 'Citation Lookup API',
                            'raw_result': result  # For debugging
                        }
                
                # No valid citations found
                return {
                    'status': 'invalid',
                    'message': f'Citation not found in database: {citation_text}',
                    'search_type': 'citation_lookup',
                    'cases': [],
                    'method': 'Citation Lookup API'
                }
            
            elif response.status_code == 400:
                return {
                    'status': 'invalid',
                    'message': f'Invalid citation format: {citation_text}',
                    'search_type': 'citation_lookup',
                    'cases': [],
                    'method': 'Citation Lookup API'
                }
            
            else:
                # API error, fall back to search
                return {
                    'status': 'error',
                    'message': f'Citation Lookup API error (status {response.status_code}): {response.text}',
                    'search_type': 'citation_lookup',
                    'cases': []
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': f'Citation Lookup API request failed: {str(e)}',
                'search_type': 'citation_lookup',
                'cases': []
            }
    
    def _enhanced_case_name_search(self, case_name, include_unpublished=False):
        """
        Enhanced case name search with better filtering and date ranges.
        Based on user's friend's suggestions for using advanced operators.
        """
        try:
            # Use advanced search operators for better results
            params = {
                'q': f'caseName:({case_name})',  # Search specifically in case name field
                'order_by': 'score desc',  # Best match first
                'format': 'json'
            }
            
            # No publication filtering - get all results and let frontend handle it
            
            print(f"DEBUG: API call params: {params}")
            
            response = requests.get(self.search_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            print(f"DEBUG: API returned {len(data.get('results', []))} results")
            if data.get('results'):
                for i, result in enumerate(data.get('results', [])[:3]):
                    print(f"  Result {i+1}: precedentialStatus='{result.get('precedentialStatus', 'MISSING')}'")
            
            results = data.get('results', [])
            
            if not results:
                # Try a broader search without field restriction
                params['q'] = case_name
                print(f"DEBUG: Broader search params: {params}")
                # Keep the same publication filter for the broader search
                response = requests.get(self.search_url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                results = data.get('results', [])
                print(f"DEBUG: Broader search returned {len(results)} results")
            
            if not results:
                return {
                    'status': 'invalid',
                    'message': f'No cases found for "{case_name}"',
                    'search_type': 'enhanced_search',
                    'cases': [],
                    'method': 'Enhanced Search API'
                }
            
            # Format the results with publication status
            cases = []
            for result in results[:5]:  # Limit to top 5 results
                # Process citations to get primary citation like Citation Lookup API
                citations = result.get('citation', [])
                primary_citation = self._get_primary_citation_from_search_result_list(citations)
                
                # Get publication status - try different possible field names
                precedential_status = (result.get('precedential_status') or 
                                     result.get('precedentialStatus') or 
                                     'unknown')  # Default to unknown for missing data
                
                # DEBUG: Add logging to see what's happening  
                print(f"  *** NEW CODE *** Raw precedential_status = '{precedential_status}'")
                
                # Get court name for publication status determination
                court_name = result.get('court', 'Unknown')
                
                # Determine if published based on actual status
                is_published = self._is_published_status(precedential_status, court_name)
                print(f"  DEBUG: is_published = {is_published}")
                
                case_info = {
                    'name': result.get('caseName', 'Unknown'),
                    'court': result.get('court', 'Unknown'),
                    'date': result.get('dateFiled', 'Unknown'),
                    'citation': primary_citation,  # Single primary citation like Citation Lookup API
                    'absolute_url': result.get('absolute_url', ''),
                    'citation_count': result.get('citeCount', 0),
                    'publication_status': precedential_status,
                    'is_published': is_published
                }
                cases.append(case_info)
            
            # Deduplicate cases by name (keep the one with highest citation count)
            cases = self._deduplicate_cases(cases)
            
            # Find the best match among all results
            if cases:
                best_match, best_similarity = self._find_best_match(case_name, cases)
                
                # If similarity is too low, warn the user
                if best_similarity < 0.8:  # 80% similarity threshold
                    return {
                        'status': 'uncertain',
                        'message': f'Found {len(results)} case(s), but best match differs from your input',
                        'search_type': 'enhanced_search',
                        'cases': cases,
                        'total_results': data.get('count', len(results)),
                        'note': f'Did you mean "{best_match["name"]}"? Your input was "{case_name}"',
                        'method': 'Enhanced Search API'
                    }
            
            return {
                'status': 'valid',
                'message': f'Found {len(results)} case(s) matching "{case_name}"',
                'search_type': 'enhanced_search',
                'cases': cases,
                'total_results': data.get('count', len(results)),
                'method': 'Enhanced Search API'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': f'Search API error: {str(e)}',
                'search_type': 'enhanced_search',
                'cases': [],
                'method': 'Enhanced Search API'
            }
    
    def _search_by_citation_parts(self, citation_parts, include_unpublished=False):
        """
        Search using parsed citation components with date filtering.
        """
        try:
            # Normalize the reporter format before searching
            normalized_reporter = self._normalize_reporter(citation_parts['reporter'])
            full_citation = f"{citation_parts['volume']} {normalized_reporter} {citation_parts['page']}"
            query = f'citation:"{full_citation}"'
            
            params = {
                'q': query,
                'order_by': 'dateFiled desc',
                'format': 'json'
            }
            
            # No publication filtering - get all results and let frontend handle it
            
            response = requests.get(self.search_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            
            if not results:
                return {
                    'status': 'invalid',
                    'message': f'No cases found for citation: {citation_parts}',
                    'search_type': 'citation_parts',
                    'cases': [],
                    'method': 'Citation Parts Search'
                }
            
            # Format results to match Citation Lookup API structure
            cases = []
            for result in results[:3]:  # Fewer results for citation searches
                # Get the primary citation for this case
                primary_citation = self._get_primary_citation_from_search_result(result, citation_parts)
                
                # Get publication status - try different possible field names
                precedential_status = (result.get('precedential_status') or 
                                     result.get('precedentialStatus') or 
                                     'unknown')  # Default to unknown for missing data
                
                # Get court name for publication status determination
                court_name = result.get('court', 'Unknown')
                
                # Determine if published based on actual status
                is_published = self._is_published_status(precedential_status, court_name)
                
                case_info = {
                    'name': result.get('caseName', 'Unknown'),
                    'court': result.get('court', 'Unknown'),
                    'date': result.get('dateFiled', 'Unknown'),
                    'citation': primary_citation,  # Single primary citation like Citation Lookup API
                    'absolute_url': result.get('absolute_url', ''),
                    'citation_count': result.get('citeCount', 0),
                    'found_citation': f"{citation_parts['volume']} {citation_parts['reporter']} {citation_parts['page']}",
                    'normalized_citation': [f"{citation_parts['volume']} {citation_parts['reporter']} {citation_parts['page']}"],
                    'publication_status': precedential_status,
                    'is_published': is_published
                }
                cases.append(case_info)
            
            return {
                'status': 'valid',
                'message': f'Valid citation found via search: {citation_parts["original"]}',
                'search_type': 'citation_parts',
                'cases': cases,
                'total_results': len(cases),
                'citation_parts': citation_parts,
                'method': 'Citation Parts Search'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': f'Citation parts search error: {str(e)}',
                'search_type': 'citation_parts',
                'cases': []
            }
    
    def _is_published_status(self, precedential_status, court_name=None):
        """
        Determine if a precedential_status indicates a published case.
        
        CourtListener precedential_status values:
        - 'Published': Published opinion (official precedent)
        - 'Precedential': Published opinion (alternative name)
        - 'Unpublished': Unpublished opinion
        - 'Unknown' or other: Treated as unpublished for safety
        
        Special handling:
        - Supreme Court cases are always considered published
        """
        print(f"    DEBUG _is_published_status: input = '{precedential_status}', court = '{court_name}'")
        
        # Special case: Supreme Court cases are always published
        if court_name and 'supreme court' in court_name.lower():
            print(f"    DEBUG _is_published_status: Supreme Court case, returning True")
            return True
        
        if not precedential_status:
            print(f"    DEBUG _is_published_status: empty/None, returning False")
            return False
        
        status = precedential_status.lower()
        result = status in ['published', 'precedential']
        print(f"    DEBUG _is_published_status: status = '{status}', result = {result}")
        # Only explicitly published cases are considered published
        return result
    
    def _deduplicate_cases(self, cases):
        """
        Remove duplicate cases by name, keeping the one with highest citation count.
        """
        if not cases:
            return cases
        
        seen_names = {}
        for case in cases:
            name = case.get('name', '').strip()
            if not name or name == 'Unknown':
                continue
                
            citation_count = case.get('citation_count', 0) or 0
            
            if name not in seen_names or citation_count > seen_names[name].get('citation_count', 0):
                seen_names[name] = case
        
        return list(seen_names.values())
    
    def _looks_like_case_name(self, text):
        """Check if text looks like a case name (contains v. or v )"""
        return bool(re.search(r'\bv\.?\s+', text, re.IGNORECASE))
    
    def _looks_like_citation_format(self, text):
        """Check if text looks like a citation format (volume reporter page)"""
        # Pattern for: number + reporter + number (like "410 US 113", "347 U.S. 483", "623 P.2d 268")
        citation_patterns = [
            r'^\d+\s+[A-Za-z.]+\d+[a-z]*\s+\d+.*$',     # "623 P.2d 268", "123 F.3d 456" 
            r'^\d+\s+[A-Za-z.]+\s+\d+.*$',              # "410 U.S. 113"
            r'^\d+\s+[A-Za-z]+\s+\d+.*$',               # "410 US 113"
        ]
        
        for pattern in citation_patterns:
            if re.match(pattern, text.strip()):
                return True
        return False
    
    def _parse_citation_parts(self, citation):
        """
        Parse citation into volume, reporter, page components.
        Enhanced version for better parsing.
        """
        # Common citation patterns
        patterns = [
            r'(\d+)\s+([A-Za-z.]+\d+[a-z]*)\s+(\d+)',           # "623 P.2d 268", "123 F.3d 456"
            r'(\d+)\s+([A-Za-z.]+)\s+(\d+)',                    # "410 U.S. 113", "410 US 113"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, citation.strip())
            if match:
                volume, reporter, page = match.groups()
                return {
                    'volume': volume.strip(),
                    'reporter': reporter.strip(),
                    'page': page.strip(),
                    'original': citation
                }
        
        return None
    
    def _normalize_reporter(self, reporter):
        """
        Normalize reporter abbreviations to standard format.
        This helps match variations like 'us', 'US', 'U.S.' to the canonical form.
        """
        reporter_lower = reporter.lower()
        
        # Common reporter normalizations
        normalizations = {
            'us': 'U.S.',
            'u.s': 'U.S.',  # Handle case where period is missing at the end
            'sct': 'S. Ct.',
            's.ct': 'S. Ct.',
            'led': 'L. Ed.',
            'l.ed': 'L. Ed.',
            'led2d': 'L. Ed. 2d',
            'l.ed.2d': 'L. Ed. 2d',
            'f2d': 'F.2d',
            'f.2d': 'F.2d',
            'f3d': 'F.3d',
            'f.3d': 'F.3d',
            'fsupp': 'F. Supp.',
            'f.supp': 'F. Supp.',
            'fsupp2d': 'F. Supp. 2d',
            'f.supp.2d': 'F. Supp. 2d',
            'fsupp3d': 'F. Supp. 3d',
            'f.supp.3d': 'F. Supp. 3d',
            'p2d': 'P.2d',
            'p.2d': 'P.2d',
            'p3d': 'P.3d',
            'p.3d': 'P.3d',
            'cal': 'Cal.',
            'cal2d': 'Cal. 2d',
            'cal.2d': 'Cal. 2d',
            'cal3d': 'Cal. 3d',
            'cal.3d': 'Cal. 3d',
            'cal4th': 'Cal. 4th',
            'cal.4th': 'Cal. 4th',
            'cal5th': 'Cal. 5th',
            'cal.5th': 'Cal. 5th',
        }
        
        # Try exact match first
        if reporter_lower in normalizations:
            return normalizations[reporter_lower]
        
        # If no exact match, return the reporter as-is but with proper capitalization
        # Handle U.S. specially since it's the most common
        if reporter_lower == 'u.s.':
            return 'U.S.'
        elif reporter_lower == 'us':
            return 'U.S.'
        elif reporter_lower.upper() == 'US':
            return 'U.S.'
        
        # For other reporters, return as-is (they might already be in correct format)
        return reporter
    
    def _calculate_similarity(self, input_text, case_name):
        """Calculate similarity between input and found case name"""
        # Normalize both strings for comparison
        input_norm = input_text.lower().strip()
        case_norm = case_name.lower().strip()
        
        # Remove common variations and extra punctuation
        input_norm = re.sub(r'[^\w\s]', '', input_norm)
        case_norm = re.sub(r'[^\w\s]', '', case_norm)
        input_norm = re.sub(r'\s+', ' ', input_norm)
        case_norm = re.sub(r'\s+', ' ', case_norm)
        
        # Check for exact match after normalization
        if input_norm == case_norm:
            return 1.0
        
        # Check if input is contained in case name (for partial matches)
        if input_norm in case_norm:
            # Bonus for containment, but not perfect score
            return 0.85 + (0.15 * SequenceMatcher(None, input_norm, case_norm).ratio())
        
        # Calculate similarity ratio
        return SequenceMatcher(None, input_norm, case_norm).ratio()
    
    def _find_best_match(self, input_text, cases):
        """Find the best matching case from the results"""
        if not cases:
            return None, 0.0
        
        best_match = None
        best_similarity = 0.0
        
        for case in cases:
            case_name = case['name']
            similarity = self._calculate_similarity(input_text, case_name)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = case
        
        return best_match, best_similarity
    
    def _get_primary_citation(self, citations):
        """Get the primary/official citation from a list of citations"""
        if not citations:
            return "No citation available"
        
        # Priority order for reporters (official first)
        reporter_priority = [
            'U.S.',      # Supreme Court official
            'Cal.',      # California official
            'Cal. 2d',
            'Cal. 3d', 
            'Cal. 4th',
            'Cal. 5th',
            'F.3d',      # Federal courts
            'F.2d', 
            'F.',
            'F. Supp. 3d',  # District courts
            'F. Supp. 2d',
            'F. Supp.',
            'S. Ct.',    # Supreme Court Reporter (West)
            'L. Ed. 2d', # Lawyer's Edition
            'L. Ed.',
            'P.2d',      # Pacific Reporter (lower priority than state official)
            'P.3d'
        ]
        
        # First, try to find citations by priority order
        for priority_reporter in reporter_priority:
            for cit in citations:
                if cit.get('reporter') == priority_reporter and cit.get('volume'):
                    return f"{cit.get('volume')} {cit.get('reporter')} {cit.get('page', '')}"
        
        # If no priority reporter found, return the first available citation
        for cit in citations:
            if cit.get('volume') and cit.get('reporter'):
                return f"{cit.get('volume')} {cit.get('reporter')} {cit.get('page', '')}"
        
        return "Citation format unavailable"
    
    def _get_primary_citation_from_search_result(self, result, citation_parts):
        """Get the primary citation from a search result, preferring the searched citation if available"""
        citations = result.get('citation', [])
        
        if not citations:
            # If no citations in result, return the searched citation
            return f"{citation_parts['volume']} {citation_parts['reporter']} {citation_parts['page']}"
        
        # Convert citation strings to a format we can parse
        citation_list = []
        if isinstance(citations, list):
            for cit_str in citations:
                # Parse citations like "623 P.2d 268" from the citation strings
                parts = cit_str.strip().split()
                if len(parts) >= 3:
                    citation_list.append({
                        'volume': parts[0],
                        'reporter': ' '.join(parts[1:-1]), 
                        'page': parts[-1]
                    })
        
        # First, check if our searched citation exists in the results
        search_citation = f"{citation_parts['volume']} {citation_parts['reporter']} {citation_parts['page']}"
        if search_citation in citations:
            return search_citation
        
        # Otherwise, use the primary citation logic
        return self._get_primary_citation(citation_list)
    
    def _get_primary_citation_from_search_result_list(self, citations):
        """Get the primary citation from a list of citation strings from search results"""
        if not citations:
            return "No citation available"
        
        # Convert citation strings to a format we can parse
        citation_list = []
        if isinstance(citations, list):
            for cit_str in citations:
                # Parse citations like "384 U.S. 436" from the citation strings
                parts = cit_str.strip().split()
                if len(parts) >= 3:
                    citation_list.append({
                        'volume': parts[0],
                        'reporter': ' '.join(parts[1:-1]), 
                        'page': parts[-1]
                    })
        
        # Use the primary citation logic
        return self._get_primary_citation(citation_list)

@click.command()
@click.argument('citation')
def main(citation: str):
    """
    Check a legal case name using the CourtListener database.
    
    Examples:
        citecheck.py "Roe v. Wade"
        citecheck.py "Brown v. Board of Education"  
        citecheck.py "Miranda v. Arizona"
    """
    try:
        checker = CitationChecker()
        
        click.echo(f"Checking: {citation}")
        click.echo("-" * 50)
        
        # Check the citation
        result = checker.check_citation(citation)
        
        if result['status'] == 'error':
            click.echo(f"Error: {result['message']}")
            return
            
        if result['status'] == 'valid':
            click.echo(f"✅ {result['message']}")
            click.echo(f"Method: {result.get('method', 'Unknown')}")
            click.echo(f"Found {result['total_results']} case(s):")
            click.echo()
            
            for i, case in enumerate(result['cases'], 1):
                click.echo(f"{i}. {case['name']}")
                if case.get('court'):
                    click.echo(f"   Court: {case['court']}")
                if case.get('date'):
                    click.echo(f"   Date Filed: {case['date']}")
                if case.get('citation'):
                    click.echo(f"   Official Citation: {case['citation']}")
                
                # Show citation lookup specific info
                if case.get('found_citation'):
                    click.echo(f"   Found Citation: {case['found_citation']}")
                if case.get('normalized_citation'):
                    click.echo(f"   Normalized: {', '.join(case['normalized_citation'])}")
                if case.get('citation_count'):
                    click.echo(f"   Times Cited: {case['citation_count']}")
                if case.get('absolute_url'):
                    click.echo(f"   URL: https://www.courtlistener.com{case['absolute_url']}")
                
                if i < len(result['cases']):
                    click.echo()
        elif result['status'] == 'invalid':
            click.echo(f"❌ {result['message']}")
            click.echo(f"Method: {result.get('method', 'Unknown')}")
        elif result['status'] == 'uncertain':
            click.echo(f"⚠️  Citation format is valid, but found {result['total_results']} general results:")
            click.echo(f"Method: {result.get('method', 'Unknown')}")
            click.echo()
            for i, case in enumerate(result['cases'], 1):
                click.echo(f"{i}. {case['name']}")
                if case.get('citations'):  # This is for the search fallback, keep as is
                    click.echo(f"   Citations: {', '.join(case['citations'])}")
                elif case.get('citation'):  # This is for citation lookup results
                    click.echo(f"   Official Citation: {case['citation']}")
                if i < len(result['cases']):
                    click.echo()
            click.echo(f"\nNote: {result['note']}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

def test_citations():
    """Test function for debugging"""
    api_key = os.getenv('COURTLISTENER_API_KEY')
    if not api_key:
        print("Error: COURTLISTENER_API_KEY not found in environment")
        return
    
    checker = CitationChecker()
    
    # Test citations
    test_citations = [
        "410 US 113",  # Roe v. Wade
        "347 US 483",  # Brown v. Board
        "999 US 999"   # Fake citation
    ]
    
    for citation in test_citations:
        print(f"\n=== Testing: {citation} ===")
        result = checker.check_citation(citation)
        
        if result['status'] == 'error':
            print(f"Error: {result['message']}")
        else:
            print(f"Status: {result['status'].upper()}")
            print(f"Search Type: {result['search_type']}")
            print(f"Message: {result['message']}")
            
            if result.get('cases'):
                print(f"\nFound Cases:")
                for i, case in enumerate(result['cases'], 1):
                    print(f"{i}. {case['name']}")
                    if case.get('court'):
                        print(f"   Court: {case['court']}")
                    if case.get('date'):
                        print(f"   Date: {case['date']}")
                    if case.get('citations'):
                        print(f"   Citations: {', '.join(case['citations'])}")
                    elif case.get('citation'):
                        print(f"   Official Citation: {case['citation']}")
                    print()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # If arguments provided, run CLI
        main()
    else:
        # Otherwise run test
        test_citations() 