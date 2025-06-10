#!/usr/bin/env python3
"""
Citation Checker Web App
Flask frontend for the CourtListener API citation checker
"""

import os
from flask import Flask, render_template, request, jsonify
from citecheck import CitationChecker
import requests

app = Flask(__name__)

@app.route('/')
def index():
    """Main page with citation input form"""
    return render_template('index.html')

@app.route('/api/check', methods=['POST'])
def check_citation():
    try:
        # Get API key from request header
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key is required in X-API-Key header'}), 401
        
        data = request.get_json()
        if not data or 'citation' not in data:
            return jsonify({'error': 'Citation text is required'}), 400
        
        citation = data['citation'].strip()
        if not citation:
            return jsonify({'error': 'Citation text cannot be empty'}), 400
        
        # Initialize the checker with user's API key
        checker = CitationChecker(api_key)
        
        # Check the citation
        result = checker.check_citation(citation)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Error checking citation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/status')
def api_status():
    """Check if the CourtListener API is accessible with user's API key"""
    try:
        # Get API key from request header
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'status': 'error', 
                'message': 'API key required',
                'api_version': 'v4'
            })
        
        # Test API connection with user's key
        headers = {'Authorization': f'Token {api_key}'}
        response = requests.get(
            'https://www.courtlistener.com/api/rest/v4/search/',
            headers=headers,
            params={'q': 'test', 'format': 'json'},
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({
                'status': 'connected', 
                'message': 'API connection successful',
                'api_version': 'v4'
            })
        elif response.status_code == 401:
            return jsonify({
                'status': 'error', 
                'message': 'Invalid API key',
                'api_version': 'v4'
            })
        else:
            return jsonify({
                'status': 'error', 
                'message': f'API returned status {response.status_code}',
                'api_version': 'v4'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': f'Connection error: {str(e)}',
            'api_version': 'v4'
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 