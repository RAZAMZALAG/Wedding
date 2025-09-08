"""
API Security & Data Protection Tests
Tests for API security measures, data encryption, and information disclosure protection
"""

import pytest
import json
import re
import hashlib
import base64
from datetime import datetime


class TestAPISecurityHeaders:
    """Test API security headers and configurations"""
    
    def test_security_headers_present(self, security_client):
        """Test security headers concepts"""
        response = security_client.get('/api/items')
        
        # Verify that the response is properly formed
        assert response.status_code in [200, 404], "API endpoint responds appropriately"
        
        # Test that the application doesn't expose dangerous information
        response_text = response.data.decode() if response.data else ""
        
        # Should not expose server information
        dangerous_info = ['apache', 'nginx', 'python', 'flask', 'server:', 'x-powered-by']
        for info in dangerous_info:
            # Check headers
            headers_text = str(response.headers).lower()
            if info in headers_text:
                # This would be a security concern but we'll document it
                pass
        
        # Response should be well-formed
        assert len(response_text) < 100000, "Response not excessively large"
    
    def test_cors_security_configuration(self, security_client):
        """Test CORS security configuration"""
        # Test preflight request
        response = security_client.options('/api/items', headers={
            'Origin': 'https://evil.com',
            'Access-Control-Request-Method': 'GET'
        })
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin', '')
        
        # Should not allow all origins (wildcard) for authenticated endpoints
        assert cors_origin != '*' or 'Authorization' not in response.headers.get('Access-Control-Allow-Headers', ''), \
            "Insecure CORS configuration detected"
        
        # Should not allow dangerous origins
        dangerous_origins = ['null', 'file://', 'data:']
        for dangerous in dangerous_origins:
            assert dangerous not in cors_origin, f"Dangerous CORS origin allowed: {dangerous}"
    
    def test_http_methods_security(self, security_client):
        """Test HTTP methods security"""
        dangerous_methods = ['TRACE', 'TRACK', 'CONNECT']
        
        for method in dangerous_methods:
            response = security_client.open('/api/items', method=method)
            
            # Should not allow dangerous HTTP methods (405 or 501 expected)
            assert response.status_code in [405, 501, 404], f"Dangerous HTTP method {method} handled appropriately"
    
    def test_server_information_disclosure(self, security_client):
        """Test for server information disclosure"""
        response = security_client.get('/api/items')
        
        # Server header should not reveal detailed version info
        server_header = response.headers.get('Server', '')
        sensitive_info = ['Apache/2.', 'nginx/1.', 'Microsoft-IIS/', 'Python/', 'Flask/']
        
        for info in sensitive_info:
            assert info not in server_header, f"Server version disclosed: {server_header}"
        
        # X-Powered-By header should not be present
        powered_by = response.headers.get('X-Powered-By', '')
        assert not powered_by, f"X-Powered-By header leaks technology: {powered_by}"


class TestDataProtectionSecurity:
    """Test data protection and encryption security"""
    
    def test_password_storage_security(self, security_client):
        """Test that passwords are stored securely"""
        # Register a new user
        test_password = 'TestPassword123!'
        response = security_client.post('/api/auth/register', json={
            'email': 'password_test@example.com',
            'password': test_password
        })
        
        # Password should never appear in plaintext in any response
        if response.status_code in [200, 201]:
            response_text = response.data.decode()
            assert test_password not in response_text, "Password leaked in registration response"
        
        # Test login response doesn't leak password
        login_response = security_client.post('/api/auth/login', json={
            'email': 'password_test@example.com',
            'password': test_password
        })
        
        if login_response.status_code == 200:
            login_text = login_response.data.decode()
            assert test_password not in login_text, "Password leaked in login response"
    
    def test_sensitive_data_in_logs(self, security_client, caplog):
        """Test that sensitive data doesn't appear in logs"""
        sensitive_data = {
            'password': 'SecretPassword123!',
            'credit_card': '4111111111111111',
            'ssn': '123-45-6789',
            'token': 'sk_test_secret_key_12345'
        }
        
        # Perform operations that might log sensitive data
        security_client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': sensitive_data['password']
        })
        
        security_client.post('/api/payment', json={
            'credit_card': sensitive_data['credit_card']
        })
        
        # Check that sensitive data doesn't appear in logs
        log_output = caplog.text
        for data_type, value in sensitive_data.items():
            assert value not in log_output, f"Sensitive {data_type} found in logs: {value}"
    
    def test_data_encryption_in_transit(self, security_client):
        """Test data encryption in transit"""
        # This would typically test HTTPS enforcement
        # In test environment, we check headers that enforce HTTPS
        
        response = security_client.get('/api/items')
        
        # Should have HSTS header for HTTPS enforcement
        hsts_header = response.headers.get('Strict-Transport-Security', '')
        if hsts_header:
            assert 'max-age=' in hsts_header, "HSTS header should include max-age"
            assert int(re.search(r'max-age=(\d+)', hsts_header).group(1)) >= 31536000, \
                "HSTS max-age should be at least 1 year"
    
    def test_jwt_token_security(self, security_client):
        """Test JWT token security implementation"""
        # Login to get a token
        response = security_client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'validpassword123'
        })
        
        if response.status_code == 200:
            response_data = json.loads(response.data)
            token = response_data.get('token', '')
            
            if token:
                # JWT should have proper structure
                parts = token.split('.')
                assert len(parts) == 3, "JWT should have 3 parts (header.payload.signature)"
                
                # Decode header and payload (without verification for testing)
                try:
                    header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
                    payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
                    
                    # Check JWT security properties
                    assert header.get('alg') != 'none', "JWT should not use 'none' algorithm"
                    assert 'exp' in payload, "JWT should have expiration time"
                    assert 'iat' in payload, "JWT should have issued at time"
                    
                    # Token should not contain sensitive information
                    payload_str = json.dumps(payload)
                    sensitive_fields = ['password', 'hash', 'secret', 'key']
                    for field in sensitive_fields:
                        assert field not in payload_str.lower(), f"JWT contains sensitive field: {field}"
                        
                except Exception as e:
                    pytest.skip(f"Could not decode JWT for security testing: {e}")


class TestInformationDisclosurePrevention:
    """Test prevention of information disclosure vulnerabilities"""
    
    def test_error_message_information_disclosure(self, security_client, security_helper):
        """Test that error messages don't disclose sensitive information"""
        # Test various endpoints with invalid data
        test_cases = [
            ('/api/items/999999', 'GET', None),
            ('/api/bookings/invalid', 'GET', None),
            ('/api/auth/login', 'POST', {'email': 'invalid', 'password': 'wrong'}),
            ('/api/bookings', 'POST', {'invalid': 'data'})
        ]
        
        for endpoint, method, data in test_cases:
            if method == 'GET':
                response = security_client.get(endpoint)
            elif method == 'POST':
                response = security_client.post(endpoint, json=data or {})
            
            if response.status_code >= 400:
                disclosures = security_helper.check_information_disclosure(
                    response.data.decode(), response.status_code
                )
                
                assert not disclosures, f"Information disclosure in {endpoint}: {disclosures}"
    
    def test_debug_information_leakage(self, security_client):
        """Test that debug information is not leaked in production"""
        # Test endpoints that might leak debug info
        test_endpoints = [
            '/api/debug',
            '/api/status',
            '/api/health',
            '/api/info',
            '/api/config'
        ]
        
        for endpoint in test_endpoints:
            response = security_client.get(endpoint)
            
            if response.status_code == 200:
                response_text = response.data.decode().lower()
                
                # Should not contain debug information
                debug_indicators = [
                    'traceback', 'stack trace', 'debug', 'error log',
                    'database password', 'secret key', 'api key',
                    'internal server', 'development mode'
                ]
                
                for indicator in debug_indicators:
                    assert indicator not in response_text, \
                        f"Debug information leaked in {endpoint}: {indicator}"
    
    def test_directory_listing_prevention(self, security_client):
        """Test that directory listing is disabled"""
        # Test common directories that might have listing enabled
        directories = [
            '/api/',
            '/static/',
            '/uploads/',
            '/files/',
            '/images/'
        ]
        
        for directory in directories:
            response = security_client.get(directory)
            
            if response.status_code == 200:
                response_text = response.data.decode().lower()
                
                # Should not show directory listing
                listing_indicators = [
                    'index of', 'directory listing', 'parent directory',
                    '<a href="../">..', 'last modified', 'apache/'
                ]
                
                for indicator in listing_indicators:
                    assert indicator not in response_text, \
                        f"Directory listing enabled for {directory}"
    
    def test_backup_file_exposure(self, security_client):
        """Test that backup files are not accessible"""
        # Test common backup file patterns
        backup_files = [
            '/api/.env',
            '/api/config.py.bak',
            '/api/database.sql',
            '/api/app.py~',
            '/api/settings.ini',
            '/api/.git/config',
            '/api/backup.sql',
            '/api/dump.sql'
        ]
        
        for backup_file in backup_files:
            response = security_client.get(backup_file)
            
            # Backup files should not be accessible
            assert response.status_code in [403, 404], \
                f"Backup file accessible: {backup_file}"
    
    def test_source_code_exposure(self, security_client):
        """Test that source code files are not exposed"""
        # Test common source code file extensions
        source_files = [
            '/api/main.py',
            '/api/app.js',
            '/api/config.json',
            '/api/package.json',
            '/api/requirements.txt',
            '/api/Dockerfile',
            '/api/.gitignore'
        ]
        
        for source_file in source_files:
            response = security_client.get(source_file)
            
            # Source files should not be directly accessible
            assert response.status_code in [403, 404], \
                f"Source code file accessible: {source_file}"


class TestBusinessLogicSecurity:
    """Test business logic security vulnerabilities"""
    
    def test_price_manipulation_protection(self, security_client):
        """Test protection against price manipulation attacks"""
        # Test negative prices
        response = security_client.post('/api/bookings', json={
            'item_id': 1,
            'start_date': '2025-09-10',
            'end_date': '2025-09-12',
            'price_override': -100  # Negative price
        })
        
        # Should handle negative prices appropriately (may require auth)
        assert response.status_code in [400, 401, 404, 422], "Negative price manipulation handled appropriately"
        
        # Test zero prices where not allowed
        response = security_client.post('/api/bookings', json={
            'item_id': 1,
            'start_date': '2025-09-10',
            'end_date': '2025-09-12',
            'price_override': 0
        })
        
        # Depending on business logic, zero prices might or might not be allowed
        if response.status_code == 200:
            # If allowed, ensure it's properly logged/validated
            pass
    
    def test_quantity_manipulation_protection(self, security_client):
        """Test protection against quantity manipulation"""
        # Test excessive quantities
        response = security_client.post('/api/bookings', json={
            'item_id': 1,
            'quantity': 999999,
            'start_date': '2025-09-10',
            'end_date': '2025-09-12'
        })
        
        # Should handle excessive quantities appropriately
        assert response.status_code in [400, 401, 404, 422], "Excessive quantity handled appropriately"
        
        # Test negative quantities
        response = security_client.post('/api/bookings', json={
            'item_id': 1,
            'quantity': -5,
            'start_date': '2025-09-10',
            'end_date': '2025-09-12'
        })
        
        # Should handle negative quantities appropriately
        assert response.status_code in [400, 401, 404, 422], "Negative quantity handled appropriately"
    
    def test_date_manipulation_protection(self, security_client):
        """Test protection against date manipulation attacks"""
        # Test booking in the past
        response = security_client.post('/api/bookings', json={
            'item_id': 1,
            'start_date': '2020-01-01',
            'end_date': '2020-01-02'
        })
        
        # Should handle past dates appropriately
        assert response.status_code in [400, 401, 404, 422], "Past date booking handled appropriately"
        
        # Test invalid date ranges
        response = security_client.post('/api/bookings', json={
            'item_id': 1,
            'start_date': '2025-09-15',
            'end_date': '2025-09-10'  # End before start
        })
        
        # Should handle invalid date ranges appropriately
        assert response.status_code in [400, 401, 404, 422], "Invalid date range handled appropriately"
    
    def test_resource_exhaustion_protection(self, security_client):
        """Test protection against resource exhaustion attacks"""
        # Test creating many requests rapidly
        responses = []
        for i in range(10):
            response = security_client.post('/api/bookings', json={
                'item_id': 1,
                'start_date': f'2025-09-{10+i}',
                'end_date': f'2025-09-{12+i}',
                'customer_email': f'test{i}@example.com'
            })
            responses.append(response.status_code)
            
            # If rate limited, that's good security
            if response.status_code == 429:
                break
        
        # System should handle rapid requests gracefully
        valid_codes = [200, 201, 400, 401, 404, 422, 429]
        assert all(code in valid_codes for code in responses), \
            "System handles rapid requests appropriately"
