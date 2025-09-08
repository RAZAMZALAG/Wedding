"""
Unit Tests for Authentication Module
Tests the auth.py functions - NO CHEATING!
"""
import pytest
from unittest.mock import patch

@pytest.mark.unit
class TestAuthFunctions:
    """Test authentication utility functions"""
    
    def test_import_auth_module(self):
        """Test that we can import the auth module"""
        try:
            import auth
            assert hasattr(auth, 'create_jwt')
            assert hasattr(auth, 'allowed_file')
        except ImportError as e:
            pytest.fail(f"Could not import auth module: {e}")
    
    def test_allowed_file_basic(self):
        """Test basic file validation"""
        try:
            import auth
            
            # Test valid file extensions
            assert auth.allowed_file('document.pdf') == True
            assert auth.allowed_file('image.jpg') == True
            assert auth.allowed_file('photo.png') == True
            assert auth.allowed_file('picture.jpeg') == True
            
            # Test invalid extensions
            assert auth.allowed_file('virus.exe') == False
            assert auth.allowed_file('script.js') == False
            assert auth.allowed_file('document.txt') == False
        except ImportError:
            pytest.skip("Auth module not available")
    
    def test_allowed_file_edge_cases(self):
        """Test edge cases for file validation"""
        from auth import allowed_file
        
        # Test files without extension
        assert allowed_file('filename') == False
        
        # Test empty filename
        assert allowed_file('') == False
        
        # Test file with multiple dots
        assert allowed_file('my.file.jpg') == True
        assert allowed_file('backup.2025.09.08.pdf') == True
        
        # Test case sensitivity
        assert allowed_file('IMAGE.JPG') == True
        assert allowed_file('DOCUMENT.PDF') == True
    
    def test_create_jwt_function(self):
        """Test JWT creation function"""
        try:
            from auth import create_jwt
            from flask import Flask
            from flask_jwt_extended import JWTManager
            
            # Create a test app with JWT configuration
            app = Flask(__name__)
            app.config['JWT_SECRET_KEY'] = 'test-secret-key'
            jwt = JWTManager(app)
            
            with app.app_context():
                # Test basic JWT creation
                token = create_jwt("test_user", 1)
                assert isinstance(token, str)
                assert len(token) > 20  # JWT tokens are typically quite long
                
                # Test with different permission levels
                token2 = create_jwt("admin_user", 3)
                assert isinstance(token2, str)
                assert token != token2  # Different users should have different tokens
                
        except ImportError:
            pytest.skip("JWT functions not available")
    
    def test_file_validation_security(self):
        """Test file validation for security"""
        from auth import allowed_file
        
        # Test potentially dangerous files
        dangerous_files = [
            'malware.exe',
            'script.bat',
            'virus.com', 
            'trojan.scr',
            'payload.dll'
        ]
        
        for dangerous_file in dangerous_files:
            assert not allowed_file(dangerous_file), f"Dangerous file {dangerous_file} should be rejected"
        
        # Test safe files
        safe_files = [
            'identity.pdf',
            'passport.jpg',
            'license.png',
            'certificate.jpeg'
        ]
        
        for safe_file in safe_files:
            assert allowed_file(safe_file), f"Safe file {safe_file} should be accepted"
        
        # Test None input
        try:
            result = allowed_file(None)
            # Should either return False or raise exception
            assert result == False
        except (AttributeError, TypeError):
            # This is also acceptable behavior
            pass
    
    @patch('auth.create_access_token')
    def test_create_jwt_function_exists(self, mock_create_token):
        """Test that create_jwt function works"""
        from auth import create_jwt
        
        mock_create_token.return_value = "fake_jwt_token"
        
        result = create_jwt(identity="test_user", permission=1)
        
        # Verify function was called
        mock_create_token.assert_called_once()
        assert result == "fake_jwt_token"
