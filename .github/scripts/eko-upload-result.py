import requests
import sys
import os
import json
from datetime import datetime

def get_scan_type(file_name):
    """Map filename to DefectDojo scan type"""
    scan_type_mapping = {
        'gitleaks-result.json': 'Gitleaks Scan',
        'gitleaks-results.json': 'Gitleaks Scan',
        'semgrep-results.json': 'Semgrep JSON Report',
        'report.json': 'Semgrep JSON Report',  
        'snyk-results.json': 'Snyk Scan',
        'trivy-results.json': 'Trivy Scan',
        'zap-results.xml': 'ZAP Scan'
    }
    
    # Get the base filename
    base_name = os.path.basename(file_name)
    return scan_type_mapping.get(base_name, 'Generic Findings Import')

def validate_file(file_path):
    """Validate that the file exists and is not empty"""
    if not os.path.exists(file_path):
        print(f'Error: File {file_path} does not exist.')
        return False
    
    if os.path.getsize(file_path) == 0:
        print(f'Warning: File {file_path} is empty. Skipping upload.')
        return False
    
    # Validate JSON files
    if file_path.endswith('.json'):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Check if it's an empty array or empty object
                if (isinstance(data, list) and len(data) == 0) or \
                   (isinstance(data, dict) and len(data) == 0):
                    print(f'Warning: File {file_path} contains no findings. Skipping upload.')
                    return False
        except json.JSONDecodeError:
            print(f'Error: File {file_path} is not valid JSON.')
            return False
    
    return True

def upload_to_defectdojo(file_path, engagement_id, defectdojo_url, token):
    """Upload scan results to DefectDojo"""
    
    if not validate_file(file_path):
        return False
    
    scan_type = get_scan_type(file_path)
    print(f'Uploading {file_path} as scan type: {scan_type}')
    
    headers = {
        'Authorization': f'Token {token}'
    }

    url = f'{defectdojo_url}/api/v2/import-scan/'

    data = {
        'active': True,
        'verified': True,
        'scan_type': scan_type,
        'minimum_severity': 'Info',  # Changed to Info to capture all findings
        'engagement': engagement_id,
        'scan_date': datetime.now().strftime('%Y-%m-%d'),
        'tags': 'automated,github-actions'
    }

    try:
        with open(file_path, 'rb') as file:
            files = {
                'file': file
            }
            
            response = requests.post(url, headers=headers, data=data, files=files, timeout=30)
            
            if response.status_code == 201:
                print(f'✅ Successfully imported {file_path} to DefectDojo')
                response_data = response.json()
                if 'test' in response_data:
                    print(f'   Test ID: {response_data["test"]}')
                return True
            else:
                print(f'❌ Failed to import {file_path}')
                print(f'   Status code: {response.status_code}')
                print(f'   Response: {response.text}')
                return False
                
    except requests.exceptions.RequestException as e:
        print(f'❌ Network error uploading {file_path}: {e}')
        return False
    except Exception as e:
        print(f'❌ Unexpected error uploading {file_path}: {e}')
        return False

def main():
    if len(sys.argv) != 2:
        print('Usage: python eko-upload-result.py <file_path>')
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Get configuration from environment variables
    token = os.environ.get('DEFECTDOJO_TOKEN')
    if not token:
        print('❌ Error: DEFECTDOJO_TOKEN environment variable is not set.')
        sys.exit(1)
    
    defectdojo_url = os.environ.get('DEFECTDOJO_URL', 'https://demo.defectdojo.org')
    engagement_id = os.environ.get('DEFECTDOJO_ENGAGEMENT_ID', '23')
    
    print(f'🔄 DefectDojo Upload Configuration:')
    print(f'   URL: {defectdojo_url}')
    print(f'   Engagement ID: {engagement_id}')
    print(f'   File: {file_path}')
    print('---')
    
    success = upload_to_defectdojo(file_path, engagement_id, defectdojo_url, token)
    
    if success:
        print('✅ Upload completed successfully')
    else:
        print('❌ Upload failed')
        sys.exit(1)

if __name__ == "__main__":
    main()